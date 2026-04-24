"""Basic tests for Research-Collector."""

import pytest
from research_collector.config import Config
from research_collector.pipeline import Pipeline


def test_config_loading():
    """Test configuration loading."""
    config = Config()
    assert config is not None
    assert config.get("time_ranges.default") == 7


def test_pipeline_initialization():
    """Test pipeline initialization."""
    config = Config()
    pipeline = Pipeline(config)
    assert pipeline is not None
    assert isinstance(pipeline.sources, dict)


def test_source_enabled():
    """Test source enablement checking."""
    config = Config()
    # Test with a source that should be enabled by default
    assert config.is_source_enabled("pubmed") == True


def test_predefined_topics():
    """Test predefined topics functionality."""
    config = Config()
    
    # Test getting all predefined topics
    all_topics = config.get_all_predefined_topics()
    assert len(all_topics) > 0
    assert "agi" in all_topics
    assert "ml" in all_topics
    
    # Test getting a specific topic
    agi_topic = config.get_predefined_topic("agi")
    assert agi_topic is not None
    assert agi_topic["name"] == "Artificial General Intelligence"
    assert len(agi_topic["keywords"]) > 0
    
    # Test getting keywords for a topic
    ml_keywords = config.get_predefined_topic_keywords("ml")
    assert ml_keywords is not None
    assert "machine learning" in ml_keywords
    
    # Test non-existent topic
    nonexistent = config.get_predefined_topic("nonexistent")
    assert nonexistent is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])