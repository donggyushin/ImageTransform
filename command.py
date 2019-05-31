"""
Author : Kyungmin Lee (rekyungmin@gmail.com)
Date : 05/30/2019
Descrip: module that process client requests
"""

import logging
from typing import Iterable

from perspective import transform
import b64image


_COMMAND = {
    'perspective': (
        ('img', str), ('cdn_x1', int), ('cdn_y1', int), ('cdn_x2', int), ('cdn_y2', int),
        ('cdn_x3', int), ('cdn_y3', int), ('cdn_x4', int), ('cdn_y4', int)
    ),
}


def _has_keys(base: dict, pairs: Iterable) -> bool:
    """
    flow
    1. check 'key in base'
    2. check 'isinstance(key, type)'
    3. cast
    """
    try:
        for key, type_class in pairs:
            if key not in base:
                return False

            if not callable(type_class):
                return False

            base[key] = type_class(base[key])

    except (ValueError, TypeError):
        return False

    return True


def handler(request: dict) -> bytes:
    if 'req' not in request:
        return 'no req'.encode()

    command = str(request['req']).strip().lower()

    logging.debug(f'request command is {command!r}')

    if command not in _COMMAND:
        logging.debug(f'invalid command {command!r}')
        return f'invalid command {command!r}'.encode()

    if command == 'perspective':
        if not _has_keys(request, _COMMAND[command]):
            return 'parameter is insufficient.'.encode()

        decoded = b64image.decode(request['img'])
        if not decoded:
            return 'image is not base64-encoded image'.encode()

        img, fmt = decoded
        coordinates = [
            (request['cdn_x1'], request['cdn_y1']),
            (request['cdn_x2'], request['cdn_y2']),
            (request['cdn_x3'], request['cdn_y3']),
            (request['cdn_x4'], request['cdn_y4']),
        ]

        transformed_img = transform(img, fmt, coordinates)

        return b64image.encode(transformed_img, fmt).encode()

