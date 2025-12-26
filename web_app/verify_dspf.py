import sys
import unittest
from unittest.mock import MagicMock
from io import BytesIO
import json

from utils import load_dspf


class TestDSPF(unittest.TestCase):
    def test_load_dspf_simple(self):
        # Create a mock DSPF/JSON content
        dspf_content = {
            "windows": [
                {
                    "type": "Plot",
                    "configuration": {
                        "channels": [{"name": "SignalA", "type": "channel"}, {"name": "SignalB", "type": "channel"}]
                    },
                },
                {"type": "Numeric", "configuration": {"channels": [{"name": "SignalC"}]}},
            ]
        }

        json_bytes = json.dumps(dspf_content).encode("utf-8")
        file_buffer = BytesIO(json_bytes)

        channels = load_dspf(file_buffer)

        self.assertEqual(channels, ["SignalA", "SignalB", "SignalC"])
        print(" - Simple DSPF load check passed")

    def test_load_dspf_nested(self):
        # Create a nested structure
        dspf_content = {
            "windows": [
                {
                    "type": "Plot",
                    "configuration": {
                        "channels": [
                            {"type": "group", "channels": [{"name": "SignalNested1"}]},
                            "SignalRawString",  # Sometimes it's just a string? Unlikely but code handles it
                        ]
                    },
                }
            ]
        }

        json_bytes = json.dumps(dspf_content).encode("utf-8")
        file_buffer = BytesIO(json_bytes)

        channels = load_dspf(file_buffer)

        self.assertIn("SignalNested1", channels)
        self.assertIn("SignalRawString", channels)
        print(" - Nested DSPF load check passed")


if __name__ == "__main__":
    unittest.main()
