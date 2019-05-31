"""
Author : Kyungmin Lee (rekyungmin@gmail.com)
Date : 05/19/2019
Descrip: Perpective transform
"""

import io
from typing import Iterable

import cv2
import numpy as np
from PIL import Image


def _transform(img: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    square_width = max(np.linalg.norm(coordinates[0] - coordinates[1]),
                       np.linalg.norm(coordinates[2] - coordinates[3]))
    square_height = max(np.linalg.norm(coordinates[0] - coordinates[3]),
                        np.linalg.norm(coordinates[1] - coordinates[2]))

    dst_coordinates = np.array([
        [0, 0],
        [square_width, 0],
        [square_width, square_height],
        [0, square_height]
    ], dtype=np.float32)

    transformation_matrix = cv2.getPerspectiveTransform(coordinates, dst_coordinates)
    return cv2.warpPerspective(img, transformation_matrix, dsize=(square_width, square_height))


def transform(bin_img: bytes, img_fmt: str, coordinates: Iterable[int]) -> bytes:
    if len(coordinates) != 4:
        raise TypeError('4 coordinates are required')

    pil_img = Image.open(io.BytesIO(bin_img))
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    np_coordinates = np.array(coordinates, dtype=np.float32)

    transformed = _transform(cv2_img, np_coordinates)
    return cv2.imencode('.' + img_fmt, transformed)[1].tobytes()


if __name__ == '__main__':
    print(cv2.__version__)  # 4.1.0
    print(np.__version__)  # 1.16.3
    print(Image.__version__)  # 6.0.0
