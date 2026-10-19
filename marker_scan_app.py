from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Scanned PDF to Markdown",
    page_icon="🔎",
    layout="centered",
)

st.markdown(
    """
    <style>
      .block-container { max-width: 880px; padding-top: 3rem; }
      [data-testid="stFileUploader"] { padding: 1rem; border-radius: 14px; }
      .quiet { color: #667085; font-size: .92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def marker_is_installed() -> bool:
    return importlib.util.find_spec("marker") is not None


@st.cache_resource(show_spinner=False)
def load_marker_models():
    """Load Marker model artifacts once and reuse them across conversions."""
    from marker.models import create_model_dict

    return create_model_dict()


def convert_scan(
    pdf_data: bytes,
    filename: str,
    mode: str,
    paginate_output: bool,
) -> tuple[str, dict]:
    """Run Marker's structured PDF pipeline with OCR forced on every page."""
    from marker.config.parser import ConfigParser
    from marker.converters.pdf import PdfConverter
    from marker.output import text_from_rendered

    config_parser = ConfigParser(
        {
            "output_format": "markdown",
            "force_ocr": True,
            "mode": mode,
            "paginate_output": paginate_output,
            # A single downloadable Markdown file cannot carry Marker's image
            # assets, so omit extraction rather than create broken image links.
            "disable_image_extraction": True,
        }
    )

    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=load_marker_models(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )

    with tempfile.TemporaryDirectory(prefix="marker-scan-") as temp_dir:
        input_path = Path(temp_dir) / Path(filename).name
        input_path.write_bytes(pdf_data)
        rendered = converter(str(input_path))

    markdown, _, _ = text_from_rendered(rendered)
    metadata = getattr(rendered, "metadata", {}) or {}
    return markdown.strip() + "\n", metadata


st.title("Scanned PDF to Markdown")
st.markdown(
    '<p class="quiet">OCR image-only PDFs with Marker and preserve headings, '
    "reading order, tables, equations, and lists where possible.</p>",
    unsafe_allow_html=True,
)

if not marker_is_installed():
    st.error("Marker is not installed in this Python environment.")
    st.code("python -m pip install -r requirements-marker.txt", language="powershell")
    st.stop()

with st.expander("Before your first conversion", expanded=False):
    st.markdown(
        "Marker downloads large model files on first use. Scanned pages also "
        "require its local inference backend. CPU conversion can be slow; a "
        "supported NVIDIA GPU is substantially faster."
    )

mode = st.selectbox(
    "Conversion mode",
    options=["fast", "balanced"],
    format_func=lambda value: (
        "Fast - recommended for CPU" if value == "fast" else "Balanced - best with a GPU"
    ),
    help="Both modes force OCR. Balanced performs more model-based layout analysis.",
)
paginate_output = st.checkbox("Add page separators to the Markdown", value=True)

upload = st.file_uploader(
    "Choose a scanned PDF",
    type=["pdf"],
    accept_multiple_files=False,
)

if upload is not None:
    if st.button("Convert scan", type="primary", use_container_width=True):
        try:
            with st.status("Running Marker OCR…", expanded=True) as status:
                st.write("Loading document models…")
                markdown, metadata = convert_scan(
                    upload.getvalue(), upload.name, mode, paginate_output
                )
                status.update(label="Conversion complete", state="complete")

            page_stats = metadata.get("page_stats", []) if isinstance(metadata, dict) else []
            st.success(
                f"Created {len(markdown):,} Markdown characters"
                + (f" from {len(page_stats)} pages." if page_stats else ".")
            )
            st.download_button(
                "Download Markdown",
                data=markdown,
                file_name=f"{Path(upload.name).stem}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            with st.expander("Preview"):
                st.code(markdown[:12000], language="markdown")
        except Exception as exc:
            st.error(f"Marker could not convert this PDF: {exc}")
            st.info(
                "If the message mentions an inference server, install the Marker "
                "backend described in the README and restart the app."
            )

st.divider()
st.caption("Processing happens locally. No LLM API or cloud OCR service is used.")
