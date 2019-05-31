"""
Author : Kyungmin Lee (rekyungmin@gmail.com)
Date : 05/30/2019
Descrip: base64-encoded image <-> (image format, binary image)
"""

import re
import base64
import binascii


def decode(b64img: str) -> tuple:
    m = re.match(r'data:image/([^;]+);base64,(.+)', b64img)
    if m is None:
        return tuple()  # empty tuple

    try:
        img = base64.b64decode(m.group(2))
    except binascii.Error:
        return tuple()  # empty tuple

    return img, m.group(1),   # (binary img, format)


def encode(img: bytes, fmt: str) -> str:
    b64img = base64.b64encode(img)
    return f'data:image/{fmt};base64,{b64img.decode()}'
