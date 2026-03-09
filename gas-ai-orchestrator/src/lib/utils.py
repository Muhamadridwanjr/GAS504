from typing import Any, Dict

def build_prompt_with_context(prompt: str, rag_contexts: list[str], extra_data: Dict[str, Any] = None) -> str:
    """Gabungkan prompt dengan konteks RAG dan data tambahan."""
    parts = []
    if rag_contexts:
        parts.append("Konteks relevan:\n" + "\n".join(rag_contexts))
    parts.append(f"Permintaan pengguna:\n{prompt}")
    if extra_data:
        parts.append("Data tambahan:\n" + "\n".join(f"{k}: {v}" for k, v in extra_data.items()))
    return "\n\n".join(parts)
