import os
import tempfile
from pathlib import Path
from typing import IO

from asammdf import MDF
import streamlit as st


@st.cache_resource
def load_mdf(file_buffer: IO[bytes]) -> tuple[MDF, str]:
    """
    Saves the uploaded file buffer to a temporary file and initializes the MDF object.
    Using a temporary file allows MDF to lazily load data, which is more memory efficient
    than loading everything into RAM.
    """
    # Create a temporary file
    # We need to delete=False because we need the path to persist for MDF to open it
    # We should handle cleanup eventually, but for this session-based approach, system cache might handle it
    # or we can track it in session state to delete later.
    suffix = Path(file_buffer.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(file_buffer.read())
        tmp_path = tmp_file.name

    try:
        mdf = MDF(tmp_path)
        return mdf, tmp_path
    except Exception as e:
        # If loading fails, we should try to clean up the temp file immediately
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
