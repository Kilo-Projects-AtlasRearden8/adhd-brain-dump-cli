"""Core data model for the ADHD brain dump CLI."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

VALID_ENERGY = ("low", "medium", "high")
VALID_URGENCY = ("low", "medium", "high")

ENERGY_RANK = {"low": 1, "medium": 2, "high": 3}
URGENCY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Item:
    """One captured brain-dump item."""

    id: str
    title: str
    energy: str = "medium"
    urgency: str = "medium"
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    done: bool = False
    done_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Item":
        return Item(
            id=data.get("id", ""),
            title=data.get("title", ""),
            energy=data.get("energy", "medium"),
            urgency=data.get("urgency", "medium"),
            tags=list(data.get("tags") or []),
            notes=data.get("notes", ""),
            created=data.get("created", ""),
            done=bool(data.get("done", False)),
            done_at=data.get("done_at"),
        )

    def priority_key(self) -> tuple:
        """Sort key: most urgent first, then highest energy, then oldest first."""
        return (
            -URGENCY_RANK.get(self.urgency, 2),
            -ENERGY_RANK.get(self.energy, 2),
            self.created,
        )
