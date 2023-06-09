from __future__ import annotations

from .Id import Id


class Label(Id):
    """Convenience class to specify constant labels."""

    def __init__(self, *labels: any):
        self.labels_ = labels

    def labels(self, labels: tuple) -> tuple:
        return self.labels_

    def __repr__(self) -> str:
        return f"Label({', '.join(repr(label) for label in self.labels_)})"
