import sys
from unittest.mock import MagicMock

import streamlit as st

# Mock streamlit session state
if not hasattr(st, "session_state"):
    st.session_state = {}  # type: ignore

# Mock MDF object
mock_mdf = MagicMock()
mock_mdf.channels_db = {"Speed": [], "RPM": [], "Torque": []}
mock_mdf.version = "4.10"

st.session_state["mdf_object"] = mock_mdf
st.session_state["selected_channels"] = ["Speed"]
st.session_state["file_path"] = "/tmp/test.mf4"

# Import component
try:
    from components import render_channel_selection

    # We just want to check if it's importable and maybe callable?
    # We can't really call it because it uses runtime streamlit calls.
    # But let's at least reference it to avoid "unused import"
    _ = render_channel_selection

    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# We can't easily run streamlit commands in a script without a runner,
# but we can check if the function exists and basic logic logic holds.
# Since we rely on st.sidebar etc which are runtime only, we skip running it.

print("Static checks passed.")
