import io

import heatshrink2
from PIL import Image, ImageOps


class Icon:
    def __init__(self, width: int, height: int, data: bytes):
        self.width = width
        self.height = height
        self.data = data

    def __str__(self) -> str:
        return f"Icon(width={self.width}, height={self.height}, data={self.data})"


def png2xbm(file_path) -> bytes:
    with Image.open(file_path) as im:
        with io.BytesIO() as output:
            bw = im.convert("1")
            bw = ImageOps.invert(bw)
            bw.save(output, format="XBM")
            return output.getvalue()


def xbm2hs(data) -> bytes:
    return heatshrink2.compress(data, window_sz2=8, lookahead_sz2=4)


def file2icon(file_path) -> Icon:
    output = png2xbm(file_path)
    assert output

    # Extract data from text
    f = io.StringIO(output.decode().strip())
    width = int(f.readline().strip().split(" ")[2])
    height = int(f.readline().strip().split(" ")[2])
    data = f.read().strip().replace("\n", "").replace(" ", "").split("=")[1][:-1]
    data_str = data[1:-1].replace(",", " ").replace("0x", "")

    data_bin = bytearray.fromhex(data_str)

    # Encode icon data with LZSS
    data_encoded_str = xbm2hs(data_bin)

    assert data_encoded_str

    data_enc = bytearray(data_encoded_str)
    data_enc = bytearray([len(data_enc) & 0xFF, len(data_enc) >> 8]) + data_enc

    # Use encoded data only if its length less than original, including header
    if len(data_enc) + 2 < len(data_bin) + 1:
        data = b"\x01\x00" + data_enc
    else:
        data = b"\x00" + data_bin

    return Icon(width, height, data)
