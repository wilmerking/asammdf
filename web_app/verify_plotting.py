import sys
from unittest.mock import MagicMock

import numpy as np

# Mock modules if they are not importable in this environment check script,
# although we should have them installed.

try:
    import plotly.graph_objects as go  # type: ignore
    from plotting import create_plot, get_plot_data
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# Mock MDF and Signal
mock_signal = MagicMock()
mock_signal.name = "TestSignal"
mock_signal.unit = "rpm"
mock_signal.timestamps = np.arange(0, 10, 0.1)  # 100 points
mock_signal.samples = np.sin(mock_signal.timestamps)
mock_signal.comment = "Test Comment"

mock_mdf = MagicMock()
mock_mdf.select.return_value = [mock_signal]

# Test Data Extraction
print("Testing get_plot_data...")
data_full = get_plot_data(mock_mdf, ["TestSignal"], decimation=1)
assert len(data_full) == 1
assert len(data_full[0]["timestamps"]) == 100
print(" - Full data extraction OK")

# Test Decimation
data_decimated = get_plot_data(mock_mdf, ["TestSignal"], decimation=10)
assert len(data_decimated[0]["timestamps"]) == 10
print(" - Decimation OK")

# Test Plot Creation
print("Testing create_plot...")
fig = create_plot(data_full)
assert isinstance(fig, go.Figure)
assert len(fig.data) == 1
print(" - Basic plot creation OK")

# Test Secondary Axis
fig_dual = create_plot([data_full[0], data_full[0]], secondary_y_channels=["TestSignal"])
# Note: Since names are same, behavior might be tricky to inspect deeply, but check trace count
assert len(fig_dual.data) == 2
print(" - Secondary axis plot creation OK")

print("Verification script finished successfully.")
