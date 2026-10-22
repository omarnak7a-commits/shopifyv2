import io
import struct
import zlib

from app.providers.base import TryOnProvider


class MockProvider(TryOnProvider):
    name = "mock"

    def generate(self, person_image_path, garment_image_url, category):
        person_bytes = b""
        if person_image_path and person_image_path.exists():
            person_bytes = person_image_path.read_bytes()

        combined = person_bytes + garment_image_url.encode("utf-8") + category.encode("utf-8")
        return _create_placeholder_png(combined)


def _create_placeholder_png(data: bytes) -> bytes:
    width, height = 512, 768
    r = (len(data) % 200) + 30
    g = (len(data) % 180) + 40
    b = (len(data) % 160) + 50

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend([r, g, b])

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    idat = _chunk(b"IDAT", zlib.compress(bytes(raw)))
    iend = _chunk(b"IEND", b"")

    buf = io.BytesIO()
    buf.write(sig)
    buf.write(ihdr)
    buf.write(idat)
    buf.write(iend)
    return buf.getvalue()
