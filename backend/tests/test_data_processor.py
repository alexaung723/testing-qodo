import pytest
import datetime
from app.data_processor import DataPoint, DataSet, DataProcessor, create_sample_data, DataVisualizer

# Test DataPoint processing

def test_datapoint_process():
    dp = DataPoint(1.0, datetime.datetime.now())
    result = dp.process()
    assert isinstance(result, float)
    # Should be marked as processed
    assert dp._processed is True
    # Second call should not change value
    result2 = dp.process()
    assert result == result2

# Test DataSet statistics

def test_dataset_statistics():
    points = [DataPoint(float(i), datetime.datetime.now()) for i in range(10)]
    ds = DataSet("test", points)
    stats = ds.get_statistics()
    assert stats["mean"] == pytest.approx(4.5)
    assert stats["min"] == 0.0
    assert stats["max"] == 9.0
    assert "median" in stats
    assert "std_dev" in stats

# Test DataProcessor add/remove/process

def test_data_processor():
    dp = DataProcessor()
    ds1 = create_sample_data(10)
    ds2 = create_sample_data(20)
    dp.add_dataset(ds1)
    dp.add_dataset(ds2)
    assert len(dp.datasets) == 2
    dp.remove_dataset(ds1.name)
    assert len(dp.datasets) == 1
    results = dp.process_all()
    assert ds2.name in results
    assert isinstance(results[ds2.name], dict)

# Test DataVisualizer

def test_data_visualizer():
    ds = create_sample_data(10)
    plot = DataVisualizer.generate_ascii_plot(ds)
    assert isinstance(plot, str)
    assert len(plot.splitlines()) > 0

# Edge case: empty dataset

def test_empty_dataset():
    ds = DataSet("empty", [])
    stats = ds.get_statistics()
    assert stats["mean"] == 0
    assert stats["min"] == 0
    assert stats["max"] == 0
    plot = DataVisualizer.generate_ascii_plot(ds)
    assert plot == "No data to plot"
