from typing import Dict, List, Tuple, Optional, Set, Any
import numpy as np
import random
from .star import Star
from .civilization import Civilization


class Universe:
    """
    Represents the universe containing stars and civilizations.

    The Universe class manages all entities in the simulation and handles
    their interactions over time.
    """

    def __init__(self, size: float = 1000.0):
        """
        Initialize a new universe.

        Args:
            size: The size of the cubic space (in arbitrary units)
        """
        self.stars: Dict[str, Star] = {}
        self.civilizations: Dict[str, Civilization] = {}
        self.current_date: float = 0
        self.size = size
        self.history: List[Dict[str, Any]] = []

    def initialize_stars(self, count: int) -> None:
        """
        Generate random stars in a cubic space.

        Args:
            count: Number of stars to generate
        """
        for i in range(count):
            # Random position in a cubic space
            position = np.random.uniform(-self.size / 2, self.size / 2, 3)

            # Random resources (higher near center, lower at edges)
            distance_from_center = np.linalg.norm(position)
            resource_base = np.random.uniform(0, 1)
            # Stars closer to center tend to have more resources
            resource_modifier = 1 - (distance_from_center / (self.size / 2)) * 0.5
            resources = min(1.0, resource_base * resource_modifier)

            # Random number of planets
            planets = np.random.geometric(p=0.2)  # Geometric distribution
            planets = min(planets, 10)  # Cap at 10 planets

            # Create the star
            star = Star(
                id=f"star_{i}",
                name=f"Star-{i}",
                position=position,
                resources=resources,
                planets=planets,
            )

            # Add to our collection
            self.stars[star.id] = star

    def add_civilization(self, civ: Civilization) -> None:
        """
        Add a new civilization to the universe.

        Args:
            civ: The civilization to add
        """
        self.civilizations[civ.params.id] = civ

        # Log the new civilization
        self._add_to_history(
            self.current_date,
            "new_civilization",
            {
                "id": civ.params.id,
                "name": civ.params.name,
                "origin_star": civ.params.origin_star.id,
            },
        )

    def remove_civilization(self, civ_id: str) -> None:
        """
        Remove a civilization from the universe (e.g., due to extinction).

        Args:
            civ_id: ID of the civilization to remove
        """
        if civ_id in self.civilizations:
            civ = self.civilizations[civ_id]
            del self.civilizations[civ_id]

            # Log the extinction
            self._add_to_history(
                self.current_date,
                "civilization_extinct",
                {
                    "id": civ_id,
                    "name": civ.params.name,
                    "existed_for": self.current_date - civ.params.founding_date,
                },
            )

    def get_star(self, star_id: str) -> Optional[Star]:
        """Get a star by ID"""
        return self.stars.get(star_id)

    def get_civilization(self, civ_id: str) -> Optional[Civilization]:
        """Get a civilization by ID"""
        return self.civilizations.get(civ_id)

    def get_nearby_stars(self, position: np.ndarray, range_limit: float) -> List[Star]:
        """
        Get stars within a certain range of a given position.

        Args:
            position: 3D position to search from
            range_limit: Maximum distance to include

        Returns:
            List of stars within the specified range
        """
        nearby = []
        for star in self.stars.values():
            distance = np.linalg.norm(star.position - position)
            if distance <= range_limit and distance > 0:  # Exclude self
                nearby.append(star)
        return nearby

    def run_simulation(self, steps: int, callback=None) -> None:
        """
        Run the simulation for a specified number of steps.

        Args:
            steps: Number of time steps to simulate
            callback: Optional callback function called after each step
        """
        for _ in range(steps):
            self.update()
            if callback:
                callback(self)

    def update(self) -> None:
        """Update the universe for one time step"""
        self.current_date += 1

        # Update all civilizations
        for civ in list(self.civilizations.values()):
            civ.update(self.current_date, self)

        # Process interactions between civilizations at same stars
        self._process_interactions()

        # Log stats
        if self.current_date % 10 == 0:
            self._log_statistics()

    def _process_interactions(self) -> None:
        """Process interactions between civilizations at the same locations"""
        # This is already handled in each civilization's update method
        pass

    def _log_statistics(self) -> None:
        """Log statistics about the current state of the universe"""
        num_civs = len(self.civilizations)
        total_population = sum(
            civ.get_total_population() for civ in self.civilizations.values()
        )

        # Count stars with civilizations
        inhabited_stars = set()
        for civ in self.civilizations.values():
            inhabited_stars.update(civ.visited_stars.keys())

        self._add_to_history(
            self.current_date,
            "statistics",
            {
                "civilizations": num_civs,
                "total_population": total_population,
                "inhabited_stars": len(inhabited_stars),
            },
        )

    def _add_to_history(
        self, date: float, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Add an event to the universe history"""
        self.history.append({"date": date, "event": event_type, "data": data})

    def get_all_civilizations(self) -> List[Civilization]:
        """Get a list of all civilizations"""
        return list(self.civilizations.values())

    def get_all_stars(self) -> List[Star]:
        """Get a list of all stars"""
        return list(self.stars.values())

    def __repr__(self) -> str:
        return f"Universe(stars={len(self.stars)}, civilizations={len(self.civilizations)}, date={self.current_date})"
