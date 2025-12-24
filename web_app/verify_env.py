import os
import tempfile

import asammdf
import plotly  # type: ignore
import streamlit
from asammdf import MDF

print(f"Streamlit version: {streamlit.__version__}")
print(f"Plotly version: {plotly.__version__}")
print(f"asammdf version: {asammdf.__version__}")

# Verify MDF creation with temp file logic
content = b"Simple Mock MDF Content"
# We can't really load a mock mdf this way without it being a valid mdf structure,
# but we can test the file handling logic.

suffix = ".mf4"
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
    tmp_file.write(content)
    tmp_path = tmp_file.name

print(f"Temp file created at: {tmp_path}")

try:
    # This will fail as it's not a real MDF, but we check if library is reachable
    print("Attempting to load invalid MDF to check import...", end=" ")
    try:
        MDF(tmp_path)
    except asammdf.blocks.utils.MdfException:
        print("Caught expected MdfException (good)")
    except Exception as e:
        print(f"Caught other exception: {type(e).__name__} (acceptable for garbage data)")

finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
        print("Temp file cleaned up.")

print("Verification script finished successfully.")
