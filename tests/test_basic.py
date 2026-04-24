"""Basic tests for Research-Collector."""

import pytest
from research_collector.config import Config
from research_collector.pipeline import Pipeline


def test_config_loading():
    """Test configuration loading."""
    config = Config()
    assert config is not None
    assert config.get("time_ranges.default") == 30


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])