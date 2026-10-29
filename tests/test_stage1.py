"""
Unit and Integration Test Suite for Stage 1 (TeleRAG 2.0)
Tests: Data Ingestion, Acronym Normalizer, Section-Aware Chunker, DEW-RRF Scoring, Hybrid Indexer.
"""
import unittest
import os
import shutil
from src.stage1_ingestion.acronym_expander import TelecomAcronymExpander
from src.stage1_ingestion.chunker import SectionAwareChunker
from src.stage1_ingestion.fetcher import TelecomDataFetcher
from src.stage1_ingestion.dew_rrf import DEWRRFScorer
from src.stage1_ingestion.indexer import TelecomHybridIndexer
from src.data_loader import TeleRAGDataLoader

class TestStage1Ingestion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.expander = TelecomAcronymExpander()
        cls.chunker = SectionAwareChunker(chunk_size_tokens=512, overlap_tokens=64)
        cls.scorer = DEWRRFScorer(alpha=0.5, beta=0.3, gamma=0.2, w_dense=0.55, w_bm25=0.45)
        cls.loader = TeleRAGDataLoader()

    def test_acronym_expansion_and_entity_extraction(self):
        query = "UE encountered PRACH collision and high BLER during T304 handover."
        entities = self.expander.extract_telecom_entities(query)
        self.assertIn("PRACH", entities)
        self.assertIn("BLER", entities)
        self.assertIn("T304", entities)

        expanded = self.expander.expand_query("Diagnose PUSCH noise floor")
        self.assertIn("Physical Uplink Shared Channel", expanded)

    def test_evidence_overlap_calculation(self):
        query = "Handover failure with T304 timer expiry in TS 38.331 section 5.3.5.3"
        doc_text = "3GPP TS 38.331 Section 5.3.5.3 specifies handover execution and timer T304."
        overlap = self.expander.get_evidence_overlap(query, doc_text)
        self.assertGreater(overlap, 0.5)

    def test_section_aware_chunker(self):
        sample_doc = (
            "# 5.3.5.3 RRC Reconfiguration\n"
            "The UE shall start timer T304 upon receiving reconfigurationWithSync.\n\n"
            "# 5.3.7.2 RLF Detection\n"
            "The UE shall start timer T310 upon receiving N310 consecutive out-of-sync indications."
        )
        chunks = self.chunker.chunk_document(sample_doc, doc_id="TS_38.331", spec_number="38.331", release="Rel-17")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].section_id, "5.3.5.3")
        self.assertEqual(chunks[1].section_id, "5.3.7.2")
        self.assertIn("T304", chunks[0].content)
        self.assertIn("T310", chunks[1].content)

    def test_dew_rrf_scoring_constraints(self):
        dense_res = [
            {"id": "doc_1", "score": 0.92, "text": "TS 38.331 T304 handover failure", "metadata": {}},
            {"id": "doc_2", "score": 0.45, "text": "TS 38.213 PUSCH power control", "metadata": {}}
        ]
        bm25_res = [
            {"id": "doc_1", "score": 8.4, "text": "TS 38.331 T304 handover failure", "metadata": {}},
            {"id": "doc_3", "score": 4.1, "text": "TS 38.413 NGAP setup", "metadata": {}}
        ]
        
        ranked = self.scorer.fuse_and_rank("T304 handover failure TS 38.331", dense_res, bm25_res)
        self.assertTrue(len(ranked) > 0)
        self.assertEqual(ranked[0]["id"], "doc_1")
        self.assertGreater(ranked[0]["dew_rrf_score"], ranked[1]["dew_rrf_score"])
        self.assertGreater(ranked[0]["evidence_match_score"], 0.0)

    def test_end_to_end_data_loader_and_search(self):
        summary = self.loader.initialize_stage1_pipeline()
        self.assertTrue(summary["indexer_ready"])
        self.assertGreater(summary["total_chunks_indexed"], 0)

        # Test TeleQnA loading
        teleqna = self.loader.load_teleqna_dataset()
        self.assertGreater(len(teleqna), 0)

        # Test Telemetry Alarm loading
        alarms = self.loader.load_telemetry_alarms()
        self.assertGreater(len(alarms), 0)

        # Test Search Retrieval
        query = "Timer T304 handover execution failure in TS 38.331"
        results = self.loader.search_3gpp_spec(query, top_k=3)
        self.assertTrue(len(results) > 0)
        top_match = results[0]
        self.assertIn("38.331", top_match["text"])
        self.assertIn("5.3.5.3", top_match["text"])

if __name__ == "__main__":
    unittest.main()
