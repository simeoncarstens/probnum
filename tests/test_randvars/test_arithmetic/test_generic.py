"""Tests for generic random variable arithmetic."""

import numpy as np
import pytest
from numpy.typing import DTypeLike

from probnum import randvars
from probnum.typing import ShapeArgType


@pytest.mark.parametrize("shape,dtype", [((5,), np.single), ((2, 3), np.double)])
def test_generic_randvar_dtype_shape_inference(shape: ShapeArgType, dtype: DTypeLike):
    x = randvars.RandomVariable(
        shape=shape, dtype=dtype, sample=lambda size, rng: np.zeros(size + shape)
    )
    y = np.array(5.0)
    z = x + y
    assert z.dtype == np.promote_types(dtype, y.dtype)
    assert z.shape == shape
