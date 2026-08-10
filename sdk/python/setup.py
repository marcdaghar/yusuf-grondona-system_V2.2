"""
Yusuf-Grondona SDK – Setup PyPI
===============================

Installation:
    pip install yusuf-grondona-sdk

License: CC BY-SA 4.0 – Marc Daghar
"""

from setuptools import setup, find_packages
import os

# Lecture du README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "SDK officiel pour le système monétaire Yusuf-Grondona"

setup(
    name="yusuf-grondona-sdk",
    version="1.0.0",
    author="Marc Daghar",
    author_email="barberoussedine@protonmail.com",
    description="SDK officiel pour l'intégration des partenaires BRI au système Yusuf-Grondona",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="CC-BY-SA-4.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "ruff>=0.1.0",
            "mypy>=1.7.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: CC BY-SA 4.0",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "yusuf",
        "grondona",
        "bri",
        "islamic-finance",
        "bimetallism",
        "zakat",
        "hisba",
        "nuqud",
        "fulus",
        "blockchain",
        "dao"
    ],
    project_urls={
        "Documentation": "https://docs.yusuf-grondona.com",
        "Source": "https://github.com/barberoussedine/yusuf-grondona-system",
        "Issue Tracker": "https://github.com/barberoussedine/yusuf-grondona-system/issues",
        "License": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
)
