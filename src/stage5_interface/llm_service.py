"""
Local LLM Service for TeleRAG 2.0 (Qwen 2.5 3B Instruct via GGUF / llama-cpp-python)
Enables offline, neural natural language generation with GPU acceleration on NVIDIA RTX 4050.
"""
import os
import sys
from typing import List, Dict, Any, Optional

# Ensure Torch CUDA DLL directory is registered so llama.dll finds cudart/cublas
try:
    import torch
    cuda_bin = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(cuda_bin) and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(cuda_bin)
except Exception:
    pass

_GLOBAL_LLM = None
_MODEL_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "models",
    "qwen2.5-3b-instruct-q4_k_m.gguf"
))


def get_llm_instance():
    """Returns singleton Llama model instance loaded onto GPU."""
    global _GLOBAL_LLM
    if _GLOBAL_LLM is not None:
        return _GLOBAL_LLM

    if not os.path.exists(_MODEL_PATH):
        print(f"[QwenLLM] Model file not found at {_MODEL_PATH}. Falling back to deterministic mode.")
        return None

    try:
        from llama_cpp import Llama
        print(f"[QwenLLM] Loading Qwen 2.5 3B from {_MODEL_PATH} with full GPU offload...")
        _GLOBAL_LLM = Llama(
            model_path=_MODEL_PATH,
            n_gpu_layers=-1,      # Offload all layers to RTX 4050 GPU VRAM
            n_ctx=2048,           # Context length for telecom prompt + 3GPP clauses
            verbose=False
        )
        print("[QwenLLM] Successfully initialized Qwen 2.5 3B on GPU.")
        return _GLOBAL_LLM
    except Exception as e:
        print(f"[QwenLLM] Failed to initialize llama_cpp: {e}")
        return None


def generate_qwen_synthesis(
    user_prompt: str,
    cited_clauses: List[Dict[str, Any]],
    ranked_causes: List[Dict[str, Any]],
    recommended_parameters: Dict[str, Any]
) -> Optional[str]:
    """
    Prompts Qwen 2.5 3B to synthesize an authoritative, natural-language engineering diagnosis
    grounded strictly in the retrieved 3GPP clauses and parameter bounds.
    """
    llm = get_llm_instance()
    if llm is None:
        return None

    # Format authoritative context
    spec_contexts = []
    for idx, c in enumerate(cited_clauses[:3], 1):
        doc = c.get("doc_id", "3GPP")
        sec = c.get("section_id", "")
        title = c.get("section_title", "")
        text = c.get("full_text") or c.get("snippet", "")
        spec_contexts.append(f"[{idx}] {doc} Section {sec} ({title}):\n{text}")

    context_str = "\n\n".join(spec_contexts)

    system_prompt = (
        "You are TeleRAG, an expert 5G/O-RAN telecommunications AI assistant pair-programming with a Network Operations Center (NOC) engineer. "
        "Your task is to generate a concise, human-understandable explanation and action summary grounded strictly in the provided 3GPP and O-RAN specification clauses.\n"
        "Rules:\n"
        "1. Do not hallucinate or use bracketed metadata tokens like [TS_...].\n"
        "2. Directly cite the relevant specification numbers (e.g. 3GPP TS 38.331 Section 5.5.4.4, O-RAN WG3 E2AP Section 8.3.1).\n"
        "3. Explain the technical chain of events clearly for the network engineer in natural professional English."
    )

    user_content = (
        f"Engineer Query: {user_prompt}\n\n"
        f"Authoritative 3GPP / O-RAN Specification Clauses:\n{context_str}\n\n"
        "Directly answer the engineer's question or doubt. "
        "If a comparison table was requested, provide a formatted markdown table. "
        "If an explanation of a specific clause or mechanism was asked, explain the exact triggers, timers, parameters, and consequences strictly based on the provided specifications."
    )

    try:
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            max_tokens=600
        )
        content = response["choices"][0]["message"]["content"].strip()
        return content
    except Exception as e:
        print(f"[QwenLLM] Generation error: {e}")
        return None
