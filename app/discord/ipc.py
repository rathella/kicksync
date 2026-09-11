from __future__ import annotations

import ctypes
import json
import msvcrt
import os
import struct
from typing import Any, Optional


class DiscordIPCError(Exception):
    """Discord IPC ile ilgili hatalar."""


class DiscordIPC:
    OP_HANDSHAKE = 0
    OP_FRAME = 1

    MAX_PIPE_NUMBER = 10

    def __init__(
        self,
        client_id: str,
    ) -> None:
        self.client_id = str(client_id)
        self.pipe: Optional[Any] = None

    @property
    def connected(self) -> bool:
        return self.pipe is not None

    def is_alive(self) -> bool:
        """Windows named pipe bağlantısının hâlâ canlı olup olmadığını kontrol eder."""
        if self.pipe is None:
            return False

        try:
            handle = msvcrt.get_osfhandle(
                self.pipe.fileno()
            )

            bytes_available = ctypes.c_ulong(0)

            result = ctypes.windll.kernel32.PeekNamedPipe(
                ctypes.c_void_p(handle),
                None,
                0,
                None,
                ctypes.byref(bytes_available),
                None,
            )

            if result:
                return True

        except (
            AttributeError,
            OSError,
            ValueError,
        ):
            pass

        self.close()
        return False

    def connect(self) -> None:
        if self.connected:
            return

        last_error: Optional[Exception] = None

        for pipe_number in range(
            self.MAX_PIPE_NUMBER
        ):
            pipe_path = (
                rf"\\?\pipe\discord-ipc-{pipe_number}"
            )

            try:
                self.pipe = open(
                    pipe_path,
                    "r+b",
                    buffering=0,
                )

                self._send(
                    self.OP_HANDSHAKE,
                    {
                        "v": 1,
                        "client_id": self.client_id,
                    },
                )

                response = self._receive()

                if response is None:
                    raise DiscordIPCError(
                        "Discord handshake cevabı alınamadı."
                    )

                return

            except (
                OSError,
                DiscordIPCError,
            ) as exc:
                last_error = exc
                self.close()

        raise DiscordIPCError(
            "Discord IPC bağlantısı bulunamadı. "
            "Discord Desktop açık mı?"
        ) from last_error

    def reconnect(self) -> None:
        self.close()
        self.connect()

    def close(self) -> None:
        if self.pipe is not None:
            try:
                self.pipe.close()
            except Exception:
                pass

        self.pipe = None

    def _send(
        self,
        opcode: int,
        payload: dict[str, Any],
    ) -> None:
        if self.pipe is None:
            raise DiscordIPCError(
                "Discord IPC bağlı değil."
            )

        encoded = json.dumps(
            payload,
            separators=(",", ":"),
        ).encode("utf-8")

        header = struct.pack(
            "<II",
            opcode,
            len(encoded),
        )

        try:
            self.pipe.write(header)
            self.pipe.write(encoded)
            self.pipe.flush()

        except OSError as exc:
            self.close()

            raise DiscordIPCError(
                "Discord IPC bağlantısı koptu."
            ) from exc

    def _receive(
        self,
    ) -> dict[str, Any]:
        if self.pipe is None:
            raise DiscordIPCError(
                "Discord IPC bağlı değil."
            )

        try:
            header = self._read_exact(8)

            opcode, length = struct.unpack(
                "<II",
                header,
            )

            payload = self._read_exact(length)

        except OSError as exc:
            self.close()

            raise DiscordIPCError(
                "Discord IPC bağlantısı koptu."
            ) from exc

        try:
            data = json.loads(
                payload.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise DiscordIPCError(
                "Discord geçersiz IPC verisi gönderdi."
            ) from exc

        data["_opcode"] = opcode

        return data

    def _read_exact(
        self,
        size: int,
    ) -> bytes:
        if self.pipe is None:
            raise DiscordIPCError(
                "Discord IPC bağlı değil."
            )

        chunks: list[bytes] = []
        remaining = size

        while remaining > 0:
            chunk = self.pipe.read(remaining)

            if not chunk:
                self.close()

                raise DiscordIPCError(
                    "Discord IPC bağlantısı kapandı."
                )

            chunks.append(chunk)
            remaining -= len(chunk)

        return b"".join(chunks)

    def send_command(
        self,
        command: str,
        args: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload = {
            "cmd": command,
            "nonce": os.urandom(16).hex(),
            "args": args or {},
        }

        try:
            self.connect()

            self._send(
                self.OP_FRAME,
                payload,
            )

            response = self._receive()

            if response is None:
                raise DiscordIPCError(
                    "Discord RPC cevabı alınamadı."
                )

            return response

        except DiscordIPCError:
            self.close()
            raise