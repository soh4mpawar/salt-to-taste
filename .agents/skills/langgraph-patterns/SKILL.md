---
name: langgraph-patterns
description: LangGraph conventions for Salt to Taste agent pipeline. Load when working on agents, graphs, LangGraph nodes, or any file in app/agents/ or app/graphs/.
---

# LangGraph Patterns for Salt to Taste

- Always use TypedDict for state definitions
- Nodes are pure functions: (state) -> dict with partial state updates
- Use Annotated fields with operator.add for list accumulation
- Compile graphs with .compile() before returning from factory functions
- Always handle Ollama connection errors with try/except and return error state
- Model names: gemma3 (parsing), deepseek-r1:8b (analysis)
- Ollama base URL comes from settings.OLLAMA_BASE_URL

## Multimodal Patterns
- Vision model: gemma3:12b (supports image input natively)
- Images must be base64 encoded before sending to Ollama
- Use PIL (Pillow) for image preprocessing — resize to max 1568px on longest side
- Tesseract is fallback for clean scanned text — try vision model first
- File uploads in FastAPI require python-multipart installed
- Always validate image format before processing: JPEG, PNG, WEBP, PDF supported
- PDF pages must be converted to images via pdf2image before vision model
