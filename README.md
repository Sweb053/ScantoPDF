# Scanned PDF to Markdown

A local Streamlit application that uses [Marker](https://github.com/datalab-to/marker) to convert scanned and image-only PDFs into structured Markdown.

## Features

- Forces OCR on every PDF page
- Fast mode for CPU systems
- Balanced mode for supported GPUs
- Preserves headings, lists, tables, and equations where possible
- Optional page separators
- Local processing with no cloud OCR or LLM API

## Requirements

- Python 3.10 or newer
- PyTorch and Marker
- A Marker inference backend: llama.cpp on CPU, or vLLM with a supported NVIDIA GPU

Marker downloads large model files on first use. CPU conversion can be slow.

## Run on Windows

Double-click `Marker Scan to Markdown.bat`, or run:

```powershell
python -m pip install -r requirements-marker.txt
python -m streamlit run marker_scan_app.py
```

## Notes

This application is intended for local or GPU-capable hosting. A basic Streamlit Community Cloud instance may not have enough memory or the required inference backend.
