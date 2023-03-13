import numpy as np
import pytest

from src.core import heatmap

travel_times = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
unique = (np.array([1,2,3,4,5]),np.array([0, 3, 5, 8, 10]))
weights = np.array([1,2,1,1,2,3,1,2,1,1,2,3])

def test_medians():
    results = heatmap.medians(travel_times, unique, weights)
    test_results = np.array([ 3. ,  7. , 16. ,  9.5, 29. ], dtype=np.float32)
    assert np.allclose(results, test_results)


def test_mins():
    results = heatmap.mins(travel_times, unique, weights)
    test_results = np.array([ 1.,  4.,  7.,  9., 22.], dtype=np.float32)
    assert np.allclose(results, test_results)

def test_counts():
    results = heatmap.counts(travel_times, unique, weights)
    test_results = np.array([3., 2., 3., 2., 2.], dtype=np.float32)
    assert np.allclose(results, test_results)

def test_averages():
    results = heatmap.averages(travel_times, unique, weights)
    test_results = np.array([2.6666667, 7., 13.666667 ,  9.5 , 29. ], dtype=np.float32)
    assert np.allclose(results, test_results) 


def test_combined_modified_gaussian_per_grid():
    sensitivity = 250000
    cuttoff = 8
    static_traveltime = 2
    results = heatmap.combined_modified_gaussian_per_grid(
        travel_times, unique, sensitivity, cuttoff, static_traveltime, weights)
    test_results = np.array([3.98570318, 2.70092096, 4.27126897, 0., 0.])
    assert np.allclose(results, test_results)
    
    
    