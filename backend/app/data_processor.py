"""
Mock Data Processing System
A complex system that processes various types of data, performs analytics,
and generates reports. This is a demo file with intentionally verbose code
to showcase Qodo Merge capabilities.
"""

import datetime
import json
import logging
import math
import random
import re
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPoint:
    """Represents a single data point in the system."""
    
    def __init__(self, value: float, timestamp: datetime.datetime, metadata: Dict = None):
        self.value = value
        self.timestamp = timestamp
        self.metadata = metadata or {}
        self._processed = False
        self._version = "1.0.0"

    def process(self) -> float:
        """Process the data point with some complex calculations."""
        if self._processed:
            return self.value
            
        # Complex processing logic
        processed_value = self.value
        for i in range(10):
            processed_value = math.sin(processed_value) + math.cos(processed_value)
            if i % 2 == 0:
                processed_value *= random.random()
            else:
                processed_value += random.random()
                
        self.value = processed_value
        self._processed = True
        return processed_value

class DataSet:
    """Represents a collection of data points."""
    
    def __init__(self, name: str, points: List[DataPoint] = None):
        self.name = name
        self.points = points or []
        self.created_at = datetime.datetime.now()
        self.modified_at = self.created_at
        self._cache = {}

    def add_point(self, point: DataPoint) -> None:
        """Add a new data point to the dataset."""
        self.points.append(point)
        self.modified_at = datetime.datetime.now()
        self._cache = {}  # Invalidate cache

    def get_statistics(self) -> Dict[str, float]:
        """Calculate various statistics for the dataset."""
        if not self.points:
            return {
                "mean": 0,
                "median": 0,
                "std_dev": 0,
                "min": 0,
                "max": 0
            }

        if "stats" in self._cache:
            return self._cache["stats"]

        values = [p.value for p in self.points]
        n = len(values)
        
        # Calculate mean
        mean = sum(values) / n
        
        # Calculate median
        sorted_values = sorted(values)
        if n % 2 == 0:
            median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            median = sorted_values[n//2]
            
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)
        
        stats = {
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "min": min(values),
            "max": max(values)
        }
        
        self._cache["stats"] = stats
        return stats

class DataProcessor:
    """Main class for processing multiple datasets."""
    
    def __init__(self):
        self.datasets: Dict[str, DataSet] = {}
        self.processing_history: List[str] = []
        self._config = {
            "max_datasets": 100,
            "cache_enabled": True,
            "debug_mode": False
        }

    def add_dataset(self, dataset: DataSet) -> None:
        """Add a new dataset to the processor."""
        if len(self.datasets) >= self._config["max_datasets"]:
            raise ValueError(f"Maximum number of datasets ({self._config['max_datasets']}) reached")
            
        if dataset.name in self.datasets:
            logger.warning(f"Dataset '{dataset.name}' already exists and will be overwritten")
            
        self.datasets[dataset.name] = dataset
        self.processing_history.append(f"Added dataset: {dataset.name}")

    def remove_dataset(self, name: str) -> None:
        """Remove a dataset from the processor."""
        if name in self.datasets:
            del self.datasets[name]
            self.processing_history.append(f"Removed dataset: {name}")
        else:
            logger.warning(f"Dataset '{name}' not found")

    def process_all(self) -> Dict[str, Dict[str, float]]:
        """Process all datasets and return their statistics."""
        results = {}
        for name, dataset in self.datasets.items():
            # Process all points
            for point in dataset.points:
                point.process()
            
            # Get statistics
            results[name] = dataset.get_statistics()
            self.processing_history.append(f"Processed dataset: {name}")
            
        return results

    def generate_report(self, format: str = "text") -> str:
        """Generate a report of all processed data."""
        if format not in ["text", "json"]:
            raise ValueError("Format must be 'text' or 'json'")

        results = self.process_all()
        
        if format == "json":
            return json.dumps(results, indent=2)
            
        # Generate text report
        report = []
        report.append("Data Processing Report")
        report.append("===================")
        report.append(f"Generated at: {datetime.datetime.now()}")
        report.append(f"Number of datasets: {len(self.datasets)}")
        report.append("")
        
        for name, stats in results.items():
            report.append(f"Dataset: {name}")
            report.append("-" * (len(name) + 9))
            for stat_name, value in stats.items():
                report.append(f"{stat_name}: {value:.2f}")
            report.append("")
            
        return "\n".join(report)

def create_sample_data(num_points: int = 100) -> DataSet:
    """Create a sample dataset with random points."""
    points = []
    now = datetime.datetime.now()
    
    for i in range(num_points):
        value = random.normalvariate(0, 1)
        timestamp = now + datetime.timedelta(minutes=i)
        metadata = {
            "index": i,
            "group": f"group_{i % 5}",
            "quality": random.random()
        }
        points.append(DataPoint(value, timestamp, metadata))
        
    return DataSet(f"sample_data_{now.strftime('%Y%m%d_%H%M%S')}", points)

class DataVisualizer:
    """Utility class for visualizing data (mock implementation)."""
    
    @staticmethod
    def generate_ascii_plot(dataset: DataSet, width: int = 60, height: int = 20) -> str:
        """Generate a simple ASCII plot of the data."""
        if not dataset.points:
            return "No data to plot"
            
        values = [p.value for p in dataset.points]
        min_val = min(values)
        max_val = max(values)
        value_range = max_val - min_val
        
        if value_range == 0:
            return "Cannot plot: all values are equal"
            
        plot = []
        for h in range(height):
            row = []
            threshold = min_val + (value_range * (height - h - 1) / height)
            for val in values:
                if val >= threshold:
                    row.append("*")
                else:
                    row.append(" ")
            plot.append("".join(row))
            
        return "\n".join(plot)

def main():
    """Example usage of the data processing system."""
    # Create processor
    processor = DataProcessor()
    
    # Create and add some sample datasets
    for i in range(3):
        dataset = create_sample_data(random.randint(50, 150))
        processor.add_dataset(dataset)
        
    # Process and generate report
    report = processor.generate_report()
    print(report)
    
    # Create visualization
    for name, dataset in processor.datasets.items():
        print(f"\nVisualization for {name}:")
        plot = DataVisualizer.generate_ascii_plot(dataset)
        print(plot)

if __name__ == "__main__":
    main()
