import numpy as np
from typing import Dict, List, Tuple, Optional


class Star:
    """
    Represents a star system in the universe.

    Attributes:
        id: Unique identifier for the star
        name: Human-readable name
        position: 3D coordinates in space
        resources: Resource level (0-1 scale of habitability/resources)
        planets: Number of planets in the system
        visiting_civilizations: Map of civilization IDs to first visit date
    """

    def __init__(
        self,
        id: str,
        name: str,
        position: np.ndarray,  # 3D vector
        resources: float,
        planets: int,
    ):
        self.id = id
        self.name = name
        self.position = position
        self.resources = resources  # 0-1 scale
        self.planets = planets
        self.visiting_civilizations: Dict[str, float] = {}

    def distance_to(self, other: "Star") -> float:
        """Calculate the distance to another star"""
        return np.linalg.norm(self.position - other.position)

    def record_visit(self, civ_id: str, date: float) -> None:
        """Record a visit by a civilization if not already recorded"""
        if civ_id not in self.visiting_civilizations:
            self.visiting_civilizations[civ_id] = date

    def get_visiting_civilizations(self) -> Dict[str, float]:
        """Get all civilizations present at this star"""
        return self.visiting_civilizations.copy()

    def __repr__(self) -> str:
        return f"Star(id={self.id}, name={self.name}, resources={self.resources:.2f}, planets={self.planets})"
