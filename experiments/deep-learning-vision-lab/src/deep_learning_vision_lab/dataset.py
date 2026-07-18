from __future__ import annotations

import numpy as np


def generate_defect_dataset(
    samples: int = 72, image_size: int = 16, seed: int = 5
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    images = rng.normal(0.18, 0.04, size=(samples, image_size, image_size)).clip(0, 1)
    labels = np.zeros(samples, dtype=int)
    for idx in range(samples):
        if idx % 3 == 1:
            row = rng.integers(2, image_size - 2)
            images[idx, row : row + 2, 2:-2] = 0.85
            labels[idx] = 1
        elif idx % 3 == 2:
            for offset in range(3, image_size - 3):
                images[idx, offset, offset] = 0.95
            labels[idx] = 2
    return images.astype("float32"), labels
