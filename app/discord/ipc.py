import json
import os
import struct
import sys
import uuid
from typing import Any, Dict, Optional


class DiscordIPC:
    OP_HANDSHAKE = 0
    OP_FRAME = 1
    OP_CLOSE = 2

    def __init__(self, client_id: str):
        self.client_id = client_id
        self._pipe = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _get_pipe_path(self, pipe_number: int = 0) -> str:
        if sys.platform == "win32":
            return rf"\\.\pipe\discord-ipc-{pipe_number}"
        else:
            temp_dir = (
                os.environ.get("XDG_RUNTIME_DIR")
                or os.environ.get("TMPDIR")
                or os.environ.get("TMP")
                or os.environ.get("TEMP")
                or "/tmp"
            )
            return os.path.join(temp_dir, f"discord-ipc-{pipe_number}")

    def connect(self) -> bool:
        if self._connected:
            return True

        for i in range(10):
            pipe_path = self._get_pipe_path(i)
            try:
                if sys.platform == "win32":
                    self._pipe = open(pipe_path, "w+b")
                else:
                    import socket
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(pipe_path)
                    self._pipe = sock
                break
            except (OSError, FileNotFoundError):
                continue
        else:
            self._connected = False
            return False

        payload = {"v": 1, "client_id": self.client_id}
        try:
            self._write_frame(self.OP_HANDSHAKE, payload)
            opcode, _ = self._read_frame()
            if opcode == self.OP_FRAME:
                self._connected = True
                return True
        except Exception:
            self.disconnect()

        return False

    def disconnect(self):
        if self._pipe:
            try:
                if sys.platform == "win32":
                    self._pipe.close()
                else:
                    self._pipe.close()
            except Exception:
                pass
            self._pipe = None
        self._connected = False

    def _write_frame(self, opcode: int, data: Dict[str, Any]):
        encoded_data = json.dumps(data).encode("utf-8")
        header = struct.pack("<II", opcode, len(encoded_data))
        if sys.platform == "win32":
            self._pipe.write(header + encoded_data)
            self._pipe.flush()
        else:
            self._pipe.sendall(header + encoded_data)

    def _read_frame(self) -> tuple[int, Dict[str, Any]]:
        if sys.platform == "win32":
            header = self._pipe.read(8)
            if len(header) < 8:
                raise ConnectionResetError("Discord bağlantısı kesildi.")
            opcode, length = struct.unpack("<II", header)
            data = self._pipe.read(length)
        else:
            header = self._pipe.recv(8)
            if len(header) < 8:
                raise ConnectionResetError("Discord bağlantısı kesildi.")
            opcode, length = struct.unpack("<II", header)
            data = b""
            while len(data) < length:
                packet = self._pipe.recv(length - len(data))
                if not packet:
                    raise ConnectionResetError("Discord bağlantısı kesildi.")
                data += packet

        return opcode, json.loads(data.decode("utf-8"))

    def send_activity(self, activity: Optional[Dict[str, Any]]) -> bool:
        if not self._connected:
            if not self.connect():
                return False

        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": os.getpid(),
                "activity": activity,
            },
            "nonce": str(uuid.uuid4()),
        }

        try:
            self._write_frame(self.OP_FRAME, payload)
            opcode, _ = self._read_frame()
            return opcode == self.OP_FRAME
        except Exception:
            self.disconnect()
            return False

    def clear_activity(self) -> bool:
        return self.send_activity(None)
