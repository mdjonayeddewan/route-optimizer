from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


class FileHandler:
    """Simple file helpers used by app and engines."""

    @staticmethod
    def read_yaml(path: str | Path) -> dict[str, Any]:
        with Path(path).open("r", encoding="utf-8") as fp:
            return yaml.safe_load(fp) or {}

    @staticmethod
    def read_csv(path: str | Path) -> pd.DataFrame:
        return pd.read_csv(path)

    @staticmethod
    def write_csv(path: str | Path, df: pd.DataFrame) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    @staticmethod
    def write_text(path: str | Path, text: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")
