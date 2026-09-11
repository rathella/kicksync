import json
import struct

from app.discord.ipc import DiscordIPC


def test_ipc_frame_format() -> None:
    payload = {
        "cmd": "SET_ACTIVITY",
        "nonce": "test",
        "args": {
            "pid": 1234,
            "activity": None,
        },
    }

    encoded = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    header = struct.pack(
        "<II",
        DiscordIPC.OP_FRAME,
        len(encoded),
    )

    opcode, length = struct.unpack(
        "<II",
        header,
    )

    assert opcode == 1
    assert length == len(encoded)


def test_ipc_payload_roundtrip() -> None:
    payload = {
        "cmd": "SET_ACTIVITY",
        "nonce": "abc123",
        "args": {},
    }

    encoded = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    decoded = json.loads(
        encoded.decode("utf-8")
    )

    assert decoded == payload