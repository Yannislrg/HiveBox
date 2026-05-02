"""Pytest configuration for HiveBox unit tests."""

from pathlib import Path
import sys
import os
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file
load_dotenv(ROOT / ".env")