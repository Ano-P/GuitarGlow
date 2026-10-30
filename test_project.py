import numpy as np
import pytest

from project import (
    normalize,
    smoothing,
    energy_mapping,
    energy_transfer,
    diffuse,
    fade,
    energy_to_rgb,
)


def test_normalize():
    assert normalize(0) == 0.0
    assert normalize(0.001) == 0.0
    assert normalize(0.09) == 1.0
    assert normalize(0.0455) == pytest.approx(0.5)


def test_smoothing():
    assert smoothing(1.0, 0.0, 0.8) == pytest.approx(0.8)
    assert smoothing(0.0, 0.8, 0.8) == pytest.approx(0.16)


def test_energy_mapping():
    assert energy_mapping(0.0) == 0.0
    assert energy_mapping(0.5) == 5.0
    assert energy_mapping(1.0) == 10.0


def test_energy_transfer():
    grid = np.zeros((5, 7))

    result = energy_transfer(grid, 3.5)

    assert result is grid
    assert grid[2, 3] == pytest.approx(3.5)

    energy_transfer(grid, 1.5)

    assert grid[2, 3] == pytest.approx(5.0)


def test_diffuse():
    grid = np.zeros((5, 5))
    grid[2, 2] = 10.0

    result = diffuse(grid)

    assert result.shape == grid.shape
    assert result[2, 2] == pytest.approx(3.0)
    assert result[1, 2] == pytest.approx(1.75)
    assert result[0, 2] == 0.0
    assert np.all(result >= 0)


def test_fade():
    grid = np.array([[2.0, 4.0], [6.0, 8.0]])

    result = fade(grid, 0.5)

    expected = np.array([[1.0, 2.0], [3.0, 4.0]])

    assert np.allclose(result, expected)


def test_energy_to_rgb():
    grid = np.zeros((360, 640))
    grid[5, 7] = 4.0
    grid[8, 9] = 20.0

    result = energy_to_rgb(grid)

    assert result.shape == (640, 360, 3)
    assert result.dtype == np.uint8
    assert np.array_equal(result[7, 5], [102, 102, 102])
    assert np.array_equal(result[9, 8], [255, 255, 255])