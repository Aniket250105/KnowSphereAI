import json
import csv
import os
from typing import List, Dict, Any

class EvaluationDataset:
    def __init__(self, filepath: str, version: str = "v1.0"):
        self.filepath = filepath
        self.version = version
        self.data: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Dataset file not found: {self.filepath}")

        ext = os.path.splitext(self.filepath)[-1].lower()
        if ext == '.json':
            self._load_json()
        elif ext == '.csv':
            self._load_csv()
        else:
            raise ValueError(f"Unsupported dataset format: {ext}")

    def _load_json(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            self._normalize_data(raw_data)

    def _load_csv(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            raw_data = []
            for row in reader:
                # Handle list conversions for expected_sources
                sources_str = row.get("expected_sources", "")
                sources = [s.strip() for s in sources_str.split(',')] if sources_str else []
                
                raw_data.append({
                    "query": row.get("query", ""),
                    "expected_answer": row.get("expected_answer", ""),
                    "expected_sources": sources,
                    "difficulty": row.get("difficulty", "medium"),
                    "category": row.get("category", "general"),
                    "dataset_version": row.get("dataset_version", self.version)
                })
            self._normalize_data(raw_data)

    def _normalize_data(self, raw_data: List[Dict[str, Any]]):
        for item in raw_data:
            self.data.append({
                "query": item.get("query", ""),
                "expected_answer": item.get("expected_answer", ""),
                "expected_sources": item.get("expected_sources", []),
                "difficulty": item.get("difficulty", "medium"),
                "category": item.get("category", "general"),
                "dataset_version": item.get("dataset_version", self.version)
            })

    def get_queries(self, profile: str = "Full") -> List[Dict[str, Any]]:
        """
        Returns a subset of the dataset based on the requested profile.
        Profiles: 'Quick' (max 25), 'Standard' (max 100), 'Full' (all).
        """
        limit = len(self.data)
        if profile.lower() == "quick":
            limit = min(25, len(self.data))
        elif profile.lower() == "standard":
            limit = min(100, len(self.data))
            
        return self.data[:limit]

    def get_version(self) -> str:
        return self.version
