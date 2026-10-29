"""
Data Loader and Stage 1 Pipeline Integration Module
TeleRAG 2.0
"""
import os
import json
from typing import List, Dict, Any, Optional
import sys
from dataclasses import dataclass

try:
    from .stage1_ingestion.acronym_expander import TelecomAcronymExpander
    from .stage1_ingestion.chunker import SectionAwareChunker, DocumentChunk
    from .stage1_ingestion.fetcher import TelecomDataFetcher
    from .stage1_ingestion.dew_rrf import DEWRRFScorer
    from .stage1_ingestion.indexer import TelecomHybridIndexer
except ImportError:
    # If run directly as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.stage1_ingestion.acronym_expander import TelecomAcronymExpander
    from src.stage1_ingestion.chunker import SectionAwareChunker, DocumentChunk
    from src.stage1_ingestion.fetcher import TelecomDataFetcher
    from src.stage1_ingestion.dew_rrf import DEWRRFScorer
    from src.stage1_ingestion.indexer import TelecomHybridIndexer

@dataclass
class TeleQnAItem:
    question_id: str
    category: str
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str

@dataclass
class SpecChunk:
    chunk_id: str
    doc_id: str
    spec_number: str
    release: str
    section_id: str
    section_title: str
    content: str
    token_count: int

@dataclass
class RANAlarmLog:
    incident_id: str
    timestamp: str
    cell_id: str
    neighbor_cell_id: Optional[str]
    severity: str
    alarm_type: str
    probable_cause: str
    kpi_snapshot: Dict[str, Any]
    raw_log: str

class TeleRAGDataLoader:
    """Unified data loader for TeleRAG 2.0."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        self.fetcher = TelecomDataFetcher(base_data_dir=self.data_dir)
        self.acronym_expander = TelecomAcronymExpander()
        self.indexer = TelecomHybridIndexer()

    def initialize_stage1_pipeline(self) -> Dict[str, Any]:
        """Runs Stage 1 data fetching, chunking, and index construction."""
        summary = self.fetcher.fetch_all()
        chunks = self.load_spec_chunks()
        doc_chunks = [
            DocumentChunk(
                chunk_id=c.chunk_id,
                doc_id=c.doc_id,
                spec_number=c.spec_number,
                release=c.release,
                section_id=c.section_id,
                section_title=c.section_title,
                content=c.content,
                token_count=c.token_count
            ) for c in chunks
        ]
        self.indexer.index_chunks(doc_chunks)
        summary["indexer_ready"] = True
        return summary

    def load_spec_chunks(self) -> List[SpecChunk]:
        """Loads processed 3GPP and O-RAN chunks from JSON."""
        processed_file = os.path.join(self.data_dir, "processed", "spec_chunks.json")
        if not os.path.exists(processed_file):
            self.fetcher.fetch_all()

        with open(processed_file, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        return [
            SpecChunk(
                chunk_id=item["chunk_id"],
                doc_id=item["doc_id"],
                spec_number=item["spec_number"],
                release=item["release"],
                section_id=item["section_id"],
                section_title=item["section_title"],
                content=item["content"],
                token_count=item["token_count"]
            )
            for item in raw_list
        ]

    def load_teleqna_dataset(self) -> List[TeleQnAItem]:
        """Loads TeleQnA benchmark items."""
        teleqna_file = os.path.join(self.data_dir, "raw", "teleqna", "teleqna_benchmark.json")
        if not os.path.exists(teleqna_file):
            self.fetcher.fetch_teleqna_benchmark()

        with open(teleqna_file, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        items = []
        for item in raw_list:
            options = {
                k: item[k] for k in ["option_1", "option_2", "option_3", "option_4"] if k in item
            }
            items.append(TeleQnAItem(
                question_id=item["question_id"],
                category=item["category"],
                question=item["question"],
                options=options,
                correct_answer=item["correct_answer"],
                explanation=item["explanation"]
            ))
        return items

    def load_telemetry_alarms(self) -> List[RANAlarmLog]:
        """Loads RAN alarm and telemetry traces."""
        alarm_file = os.path.join(self.data_dir, "raw", "telemetry", "ran_incident_logs.json")
        if not os.path.exists(alarm_file):
            self.fetcher.fetch_ran_telemetry_and_alarms()

        with open(alarm_file, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        return [
            RANAlarmLog(
                incident_id=item["incident_id"],
                timestamp=item["timestamp"],
                cell_id=item["cell_id"],
                neighbor_cell_id=item.get("neighbor_cell_id"),
                severity=item["severity"],
                alarm_type=item["alarm_type"],
                probable_cause=item["probable_cause"],
                kpi_snapshot=item["kpi_snapshot"],
                raw_log=item["raw_log"]
            )
            for item in raw_list
        ]

    def search_3gpp_spec(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves authoritative 3GPP clauses using DEW-RRF scoring."""
        return self.indexer.search(query, top_k=top_k)


if __name__ == "__main__":
    loader = TeleRAGDataLoader()
    summary = loader.initialize_stage1_pipeline()
    print("Stage 1 Pipeline Initialized Successfully:")
    print(summary)
    
    # Test query
    sample_query = "Why did handover execution fail due to T304 timer expiry in TS 38.331?"
    print(f"\nTesting DEW-RRF Retrieval for: '{sample_query}'")
    results = loader.search_3gpp_spec(sample_query, top_k=3)
    for i, res in enumerate(results, 1):
        print(f"\n[Rank {i}] DEW-RRF Score: {res['dew_rrf_score']:.4f} | Evidence Score E(q,d): {res['evidence_match_score']:.2f}")
        print(f"Doc: {res['metadata'].get('doc_id')} §{res['metadata'].get('section_id')} - {res['metadata'].get('section_title')}")
        print(f"Snippet: {res['text'][:140]}...")
