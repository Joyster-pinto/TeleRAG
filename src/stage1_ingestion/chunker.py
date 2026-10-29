"""
Hierarchical Section-Aware Token Chunker & Metadata Enricher for 3GPP & O-RAN Specifications
Implements:
1. Hierarchical Section Parser (L = 512 tokens / o = 64 overlap)
2. Metadata Enrichment (Section, Layer, Release, Spec ID)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import re


@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str                   # e.g., "TS_38.331"
    spec_number: str              # e.g., "38.331"
    release: str                  # e.g., "Rel-17"
    section_id: str               # e.g., "5.3.5.3"
    section_title: str            # e.g., "RRC Reconfiguration - Handover Execution"
    content: str                  # Clean text chunk
    token_count: int              # Approximate token count
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "spec_number": self.spec_number,
            "release": self.release,
            "section_id": self.section_id,
            "section_title": self.section_title,
            "content": self.content,
            "token_count": self.token_count,
            "metadata": self.metadata
        }


class SectionAwareChunker:
    """
    Parses hierarchical technical documents and produces 512-token chunks with 64-token overlap.
    Enriches each chunk with Section, Protocol Layer, Release, and Spec ID metadata.
    """

    SPEC_LAYER_MAP: Dict[str, str] = {
        "38.331": "MOBILITY_RRC",
        "38.213": "PHY_QUALITY",
        "38.211": "PHY_QUALITY",
        "38.413": "CORE_TRANSPORT",
        "28.541": "SON_OPTIMIZATION",
        "O-RAN.WG3.E2AP": "ORAN_INTERFACE"
    }

    def __init__(self, chunk_size_tokens: int = 512, overlap_tokens: int = 64):
        self.chunk_size = chunk_size_tokens
        self.overlap = overlap_tokens

    def _approx_token_count(self, text: str) -> int:
        words = text.split()
        return int(len(words) * 1.33)

    def _infer_layer(self, spec_number: str) -> str:
        return self.SPEC_LAYER_MAP.get(spec_number, "SPEC_QNA")

    def _parse_header_line(self, line: str) -> Optional[Tuple[str, str]]:
        stripped = line.strip()
        m_num = re.match(r'^(?:#{1,6}\s*)?(\d+(?:\.\d+)+)\s*(.*)$', stripped)
        if m_num:
            sec_id = m_num.group(1).strip()
            title = m_num.group(2).strip() or "Specification Section"
            return (sec_id, title)

        m_hash = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if m_hash and len(stripped) < 100:
            title = m_hash.group(2).strip()
            return ("1.0", title)

        return None

    def chunk_document(
        self,
        raw_text: str,
        doc_id: str,
        spec_number: str = "38.331",
        release: str = "Rel-17"
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []

        lines = raw_text.splitlines()
        current_section_id = "1.0"
        current_section_title = "General Overview"
        section_buffer: List[str] = []

        sections: List[Dict[str, Any]] = []

        for line in lines:
            header_match = self._parse_header_line(line)
            if header_match:
                if section_buffer:
                    sections.append({
                        "section_id": current_section_id,
                        "section_title": current_section_title,
                        "text": "\n".join(section_buffer)
                    })
                    section_buffer = []
                current_section_id, current_section_title = header_match
            else:
                section_buffer.append(line)

        if section_buffer:
            sections.append({
                "section_id": current_section_id,
                "section_title": current_section_title,
                "text": "\n".join(section_buffer)
            })

        chunk_idx = 0
        protocol_layer = self._infer_layer(spec_number)

        for sec in sections:
            sec_text = sec["text"].strip()
            if not sec_text:
                continue

            words = sec_text.split()
            words_per_chunk = int(self.chunk_size / 1.33)
            words_overlap = int(self.overlap / 1.33)
            step = max(1, words_per_chunk - words_overlap)

            enriched_meta = {
                "header": f"{doc_id} §{sec['section_id']}",
                "section": sec["section_id"],
                "layer": protocol_layer,
                "release": release,
                "spec_id": doc_id,
                "doc_id": doc_id,
                "spec_number": spec_number
            }

            if len(words) <= words_per_chunk:
                chunk_id = f"{doc_id}_{sec['section_id']}_{chunk_idx}"
                formatted_content = f"[{doc_id} {release} §{sec['section_id']} {sec['section_title']}]\n{sec_text}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    spec_number=spec_number,
                    release=release,
                    section_id=sec["section_id"],
                    section_title=sec["section_title"],
                    content=formatted_content,
                    token_count=self._approx_token_count(formatted_content),
                    metadata=dict(enriched_meta)
                ))
                chunk_idx += 1
            else:
                for w_start in range(0, len(words), step):
                    w_end = min(len(words), w_start + words_per_chunk)
                    chunk_words = words[w_start:w_end]
                    chunk_text = " ".join(chunk_words)

                    chunk_id = f"{doc_id}_{sec['section_id']}_{chunk_idx}"
                    formatted_content = f"[{doc_id} {release} §{sec['section_id']} {sec['section_title']} (Part {chunk_idx+1})]\n{chunk_text}"

                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        spec_number=spec_number,
                        release=release,
                        section_id=sec["section_id"],
                        section_title=sec["section_title"],
                        content=formatted_content,
                        token_count=self._approx_token_count(formatted_content),
                        metadata=dict(enriched_meta)
                    ))
                    chunk_idx += 1
                    if w_end >= len(words):
                        break

        return chunks
