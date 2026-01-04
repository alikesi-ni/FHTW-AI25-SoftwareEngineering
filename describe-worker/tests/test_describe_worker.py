import os
import sys
from pathlib import Path

import httpx

# Make sure the project root (the directory containing describe_worker.py) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from describe_worker import gemini_caption


class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


def test_gemini_caption_extracts_text(monkeypatch):
    # Arrange
    os.environ["GEMINI_API_KEY"] = "test-key"

    fake_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "A small orange cartoon creature holding a flame."}
                    ]
                }
            }
        ]
    }

    def fake_post(self, url, headers=None, json=None):
        # Basic sanity checks on payload
        parts = json["contents"][0]["parts"]
        assert "inlineData" in parts[0]
        assert "text" in parts[1]
        return DummyResponse(fake_response)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    image_bytes = b"fake-image-bytes"
    mime_type = "image/png"
    prompt = "Describe this image."

    # Act
    caption = gemini_caption(image_bytes, mime_type, prompt)

    # Assert
    assert caption == "A small orange cartoon creature holding a flame."
