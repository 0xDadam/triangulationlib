"""Pytest configuration for the triangulationlib integration tests.

Adds the project root to sys.path so that both the pure-Python
``triangulation_python`` package and the native modules installed
via pip into the conda environment (``delaunay_rust``, ``delaunay_cpp``)
are importable when tests are invoked from any working directory.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))