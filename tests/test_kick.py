from datetime import timezone

from app.kick.client import KickClient


def test_offline_channel() -> None:
    client = KickClient(
        "https://kick.com/testuser"
    )

    data = {
        "livestream": None
    }

    stream = client._parse_channel(data)

    assert stream.is_live is False
    assert stream.username == "testuser"


def test_live_channel() -> None:
    client = KickClient(
        "https://kick.com/testuser"
    )

    data = {
        "livestream": {
            "is_live": True,
            "session_title": "Test Yayını",
            "viewer_count": 1234,
            "start_time": "2026-09-11 00:00:00",
            "categories": [
                {
                    "name": "Just Chatting"
                }
            ],
            "thumbnail": "https://example.com/test.jpg",
        }
    }

    stream = client._parse_channel(data)

    assert stream.is_live is True
    assert stream.title == "Test Yayını"
    assert stream.category == "Just Chatting"
    assert stream.viewers == 1234
    assert stream.thumbnail_url == (
        "https://example.com/test.jpg"
    )
    assert stream.started_at is not None
    assert stream.started_at.tzinfo == timezone.utc


def test_invalid_datetime() -> None:
    client = KickClient(
        "https://kick.com/testuser"
    )

    result = client._parse_datetime(
        "gecersiz-tarih"
    )

    assert result is None