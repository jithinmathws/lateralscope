from __future__ import annotations

import json
from pathlib import Path

from app.graph.types import EdgeData, NodeData


class GraphDataLoader:
    """
    Loads graph input data from JSON files and converts them
    into typed NodeData and EdgeData objects.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)

    def load_nodes(self, filename: str = "nodes.json") -> list[NodeData]:
        raw_nodes = self._load_json_array(filename)
        return [NodeData(**node) for node in raw_nodes]

    def load_edges(self, filename: str = "edges.json") -> list[EdgeData]:
        raw_edges = self._load_json_array(filename)
        return [EdgeData(**edge) for edge in raw_edges]

    def _load_json_array(self, filename: str) -> list[dict]:
        path = self.data_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError(f"{filename} must contain a JSON array.")

        return payload