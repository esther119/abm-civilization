from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set, Any
import numpy as np
import random


@dataclass
class CivilizationParams:
    """Parameters defining a civilization's characteristics"""

    id: str
    name: str
    origin_star: "Star"
    # Population parameters
    population: float
    reproduction_rate: float
    individual_lifespan: float
    # Expansion parameters
    expansion_rate: float
    expansion_range: float
    # Interaction parameters
    cooperation_factor: float  # 0-1 scale
    aggression_factor: float  # 0-1 scale
    # Development parameters
    founding_date: float
    tech_level: float
    tech_advancement_rate: float
    # Advanced parameters
    time_horizon: float
    biological_type: str  # 'biological', 'artificial', 'hybrid'
    organization_type: str  # 'individual', 'hive', 'singular'
    motivation: str  # 'expansion', 'knowledge', 'seeding', 'resource'


class Civilization:
    """
    Represents a civilization that can expand across star systems and interact with other civilizations.

    Each civilization has specific characteristics defined by its parameters, and its state
    changes over time as it grows, expands, and interacts with others.
    """

    def __init__(self, params: CivilizationParams):
        self.params = params
        self.visited_stars: Dict[str, float] = {
            params.origin_star.id: params.founding_date
        }
        self.colonies: Dict[str, float] = {}  # Star ID -> population at that star
        self.colonies[params.origin_star.id] = params.population
        self.history: List[Dict[str, Any]] = []
        self.tech_history: List[Tuple[float, float]] = [
            (params.founding_date, params.tech_level)
        ]
        self.population_history: List[Tuple[float, float]] = [
            (params.founding_date, params.population)
        ]

        # Record the initial visit to the origin star
        params.origin_star.record_visit(params.id, params.founding_date)

        # Log founding event
        self._add_to_history(
            params.founding_date,
            "founding",
            {
                "star": params.origin_star.id,
                "tech_level": params.tech_level,
                "population": params.population,
            },
        )

    def update(self, current_date: float, universe: "Universe") -> None:
        """Update the civilization for one time step"""
        self._update_population(current_date, universe)
        self._update_technology(current_date)
        self._expand_to_new_stars(current_date, universe)
        self._interact_with_other_civilizations(current_date, universe)

    def _update_population(self, current_date: float, universe: "Universe") -> None:
        """Update population across all colonies"""
        total_population = 0

        # Update each colony's population
        for star_id, population in list(self.colonies.items()):
            # Get the star's resource level
            star = universe.get_star(star_id)
            if star is None:
                continue

            # Population growth is affected by reproduction rate, lifespan, and resources
            growth_rate = self.params.reproduction_rate - (
                1 / self.params.individual_lifespan
            )

            # Apply resource constraints - lower resources reduce growth
            effective_growth_rate = growth_rate * star.resources

            # Calculate new population
            new_population = population * (1 + effective_growth_rate)

            # Apply carrying capacity based on star resources
            carrying_capacity = star.resources * 1e9 * star.planets
            if new_population > carrying_capacity:
                new_population = carrying_capacity

            # Update the colony population
            self.colonies[star_id] = new_population
            total_population += new_population

        # Update the main population parameter
        self.params.population = total_population

        # Record population history
        self.population_history.append((current_date, total_population))

    def _update_technology(self, current_date: float) -> None:
        """Update the civilization's technology level"""
        # Basic technological advancement
        new_tech_level = self.params.tech_level * (
            1 + self.params.tech_advancement_rate
        )

        # Adjust based on motivation
        if self.params.motivation == "knowledge":
            # Knowledge-focused civilizations advance tech faster
            new_tech_level *= 1.2

        self.params.tech_level = new_tech_level

        # Record tech history
        self.tech_history.append((current_date, new_tech_level))

    def _expand_to_new_stars(self, current_date: float, universe: "Universe") -> None:
        """Attempt to expand to new stars based on expansion parameters"""
        # Skip expansion if not ready
        if current_date - self.params.founding_date < 10:  # Minimum establishment time
            return

        # Try expansion from each visited star
        for origin_star_id in list(self.visited_stars.keys()):
            origin_star = universe.get_star(origin_star_id)
            if origin_star is None:
                continue

            # Get candidate stars for expansion
            candidate_stars = universe.get_nearby_stars(
                position=origin_star.position,
                range_limit=self.params.expansion_range * self.params.tech_level,
            )

            # Filter out already visited stars
            candidate_stars = [
                s for s in candidate_stars if s.id not in self.visited_stars
            ]

            # No candidates, skip
            if not candidate_stars:
                continue

            # Try to expand to each candidate based on expansion rate
            for star in candidate_stars:
                # Probability of successful expansion
                distance = origin_star.distance_to(star)

                # Skip if beyond range
                if distance > self.params.expansion_range * self.params.tech_level:
                    continue

                # Adjust for tech level and distance
                probability = self.params.expansion_rate * (
                    1
                    - distance / (self.params.expansion_range * self.params.tech_level)
                )

                # Adjust for star resources
                probability *= star.resources

                # Adjust for motivation
                if self.params.motivation == "expansion":
                    probability *= 1.5
                elif self.params.motivation == "seeding":
                    probability *= 1.3
                elif self.params.motivation == "resource":
                    # Resource-focused only expands to resource-rich stars
                    if star.resources < 0.6:
                        probability *= 0.2

                # Attempt expansion
                if random.random() < probability:
                    # Success! Mark star as visited
                    self.visited_stars[star.id] = current_date
                    star.record_visit(self.params.id, current_date)

                    # Establish a colony with a portion of the origin star's population
                    origin_population = self.colonies.get(origin_star_id, 0)
                    colony_size = origin_population * 0.1  # 10% of origin population
                    self.colonies[origin_star_id] = origin_population - colony_size
                    self.colonies[star.id] = colony_size

                    # Log the expansion
                    self._add_to_history(
                        current_date,
                        "expansion",
                        {
                            "from_star": origin_star_id,
                            "to_star": star.id,
                            "distance": distance,
                            "colony_size": colony_size,
                        },
                    )

                    # Limit expansions per turn to prevent explosive growth
                    if len(self.visited_stars) % 10 == 0:
                        return

    def _interact_with_other_civilizations(
        self, current_date: float, universe: "Universe"
    ) -> None:
        """Handle interactions with other civilizations"""
        # Check each star we've visited for other civilizations
        for star_id in self.visited_stars:
            star = universe.get_star(star_id)
            if star is None:
                continue

            # Get other civilizations at this star
            visitors = star.get_visiting_civilizations()

            # Remove ourselves from the list
            if self.params.id in visitors:
                del visitors[self.params.id]

            # No other civilizations here
            if not visitors:
                continue

            # Interact with each other civilization
            for other_civ_id, visit_date in visitors.items():
                other_civ = universe.get_civilization(other_civ_id)
                if other_civ is None:
                    continue

                # Both civilizations must be established at this star (not just passing through)
                if star_id not in other_civ.colonies or star_id not in self.colonies:
                    continue

                # Determine interaction type based on cooperation and aggression factors
                if self.params.cooperation_factor > self.params.aggression_factor:
                    # Peaceful interaction
                    self._peaceful_interaction(current_date, other_civ, star)
                else:
                    # Hostile interaction
                    self._hostile_interaction(current_date, other_civ, star, universe)

    def _peaceful_interaction(
        self, current_date: float, other_civ: "Civilization", star: "Star"
    ) -> None:
        """Handle peaceful interaction between civilizations"""
        # Technology exchange
        if other_civ.params.tech_level > self.params.tech_level:
            # We learn from more advanced civilization
            tech_boost = (
                (other_civ.params.tech_level - self.params.tech_level)
                * self.params.cooperation_factor
                * 0.1
            )
            self.params.tech_level += tech_boost

            self._add_to_history(
                current_date,
                "tech_exchange",
                {
                    "with_civilization": other_civ.params.id,
                    "at_star": star.id,
                    "tech_boost": tech_boost,
                },
            )

    def _hostile_interaction(
        self,
        current_date: float,
        other_civ: "Civilization",
        star: "Star",
        universe: "Universe",
    ) -> None:
        """Handle hostile interaction between civilizations"""
        # Determine relative strength (combination of tech level and local population)
        our_population = self.colonies.get(star.id, 0)
        their_population = other_civ.colonies.get(star.id, 0)

        our_strength = our_population * self.params.tech_level
        their_strength = their_population * other_civ.params.tech_level

        # Combine with aggression factors
        our_effective_strength = our_strength * self.params.aggression_factor
        their_effective_strength = their_strength * other_civ.params.aggression_factor

        # Determine winner
        if our_effective_strength > their_effective_strength:
            # We win
            captured_population = (
                their_population * 0.5
            )  # Capture half their population
            self.colonies[star.id] += captured_population
            other_civ.colonies[star.id] -= captured_population

            self._add_to_history(
                current_date,
                "conflict_won",
                {
                    "against_civilization": other_civ.params.id,
                    "at_star": star.id,
                    "captured_population": captured_population,
                },
            )

            # If we completely defeated them at this location
            if other_civ.colonies[star.id] <= 100:  # Minimum viable population
                other_civ.colonies.pop(star.id)

                # If this was their last colony, they're extinct
                if not other_civ.colonies:
                    universe.remove_civilization(other_civ.params.id)
                    self._add_to_history(
                        current_date,
                        "extinction_caused",
                        {"civilization": other_civ.params.id},
                    )
        else:
            # They win
            lost_population = our_population * 0.5  # Lose half our population
            other_civ.colonies[star.id] += lost_population
            self.colonies[star.id] -= lost_population

            self._add_to_history(
                current_date,
                "conflict_lost",
                {
                    "against_civilization": other_civ.params.id,
                    "at_star": star.id,
                    "lost_population": lost_population,
                },
            )

            # If we were completely defeated at this location
            if self.colonies[star.id] <= 100:  # Minimum viable population
                self.colonies.pop(star.id)

                # If this was our last colony, we're extinct
                if not self.colonies:
                    universe.remove_civilization(self.params.id)
                    self._add_to_history(
                        current_date, "extinction", {"caused_by": other_civ.params.id}
                    )

    def _add_to_history(
        self, date: float, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Add an event to the civilization's history"""
        self.history.append({"date": date, "event": event_type, "data": data})

    def get_total_population(self) -> float:
        """Get the total population across all colonies"""
        return sum(self.colonies.values())

    def __repr__(self) -> str:
        return f"Civilization(id={self.params.id}, name={self.params.name}, stars={len(self.visited_stars)}, tech={self.params.tech_level:.2f})"
