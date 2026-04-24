"""
Research-Collector: Educational multi-source research aggregation tool

Aggregates information from academic, professional, social, and news sources
with engagement-based ranking and flexible time windows for educational purposes.
"""

__version__ = "1.0.0"
__author__ = "Education Community"
__license__ = "MIT"

from research_collector.config import Config
from research_collector.pipeline import Pipeline

__all__ = ["Config", "Pipeline"]