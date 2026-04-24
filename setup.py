"""Setup configuration for Research-Collector."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="research-collector",
    version="1.0.0",
    author="Education Community",
    author_email="education@example.com",
    description="Educational multi-source research aggregation tool for learning and teaching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/education/research-collector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "requests>=2.32.0",
        "pyyaml>=6.0.0",
        "python-dateutil>=2.8.0",
        "feedparser>=6.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "rich>=13.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "academic": [
            "biopython>=1.83.0",
        ],
        "huggingface": [
            "huggingface_hub>=0.19.0",
            "datasets>=2.14.0",
        ],
        "web": [
            "flask>=2.3.0",
        ],
        "all": [
            "biopython>=1.83.0",
            "huggingface_hub>=0.19.0",
            "datasets>=2.14.0",
            "flask>=2.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "research-collector=research_collector.cli:main",
        ],
    },
)