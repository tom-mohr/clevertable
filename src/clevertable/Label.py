from __future__ import annotations

from .Id import Id


class Label(Id):
    """Convenience class to specify constant labels."""

    def __init__(self, *labels: any):
        self.labels_ = list(labels)

    def labels(self, labels: list) -> list:
        return self.labels_

    def __repr__(self) -> str:
        if len(self.labels_) == 1:
            # prefer Label("foo") representation over ("foo",)
            return f"Label({repr(self.labels_[0])})"

        # tuples are parsed to Label()
        return repr(tuple(self.labels_))
