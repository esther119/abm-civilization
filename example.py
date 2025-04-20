#!/usr/bin/env python3
"""
Example script for running a simple civilization simulation.

This script shows a minimal example of setting up and running
the interstellar civilization simulation.
"""

import numpy as np
import matplotlib.pyplot as plt
from models import Universe, Civilization, CivilizationParams
from simulation import UniverseVisualizer


def main():
    # Create a universe with a smaller number of stars for faster execution
    universe = Universe(size=500.0)
    universe.initialize_stars(300)

    # Find a star with good resources for the first civilization
    stars = sorted(universe.get_all_stars(), key=lambda s: s.resources, reverse=True)
    star1 = stars[0]

    # Create a cooperative, expansion-focused civilization
    civ1_params = CivilizationParams(
        id="civ_1",
        name="Explorers",
        origin_star=star1,
        population=1e6,
        reproduction_rate=0.01,
        individual_lifespan=100,
        expansion_rate=0.08,  # High expansion rate
        expansion_range=100,
        cooperation_factor=0.7,  # Cooperative
        aggression_factor=0.3,
        founding_date=0,
        tech_level=1.0,
        tech_advancement_rate=0.005,
        time_horizon=1000,
        biological_type="biological",
        organization_type="individual",
        motivation="expansion",  # Focused on expansion
    )
    civ1 = Civilization(civ1_params)
    universe.add_civilization(civ1)

    # Create a knowledge-focused civilization
    star2 = stars[10]  # Use a different star
    civ2_params = CivilizationParams(
        id="civ_2",
        name="Scholars",
        origin_star=star2,
        population=8e5,
        reproduction_rate=0.008,
        individual_lifespan=120,
        expansion_rate=0.03,  # Lower expansion rate
        expansion_range=80,
        cooperation_factor=0.8,  # Very cooperative
        aggression_factor=0.2,
        founding_date=0,
        tech_level=1.2,  # Start with higher tech
        tech_advancement_rate=0.01,  # Faster tech advancement
        time_horizon=1500,
        biological_type="hybrid",
        organization_type="hive",
        motivation="knowledge",  # Focused on knowledge
    )
    civ2 = Civilization(civ2_params)
    universe.add_civilization(civ2)

    # Create an aggressive, resource-focused civilization
    star3 = stars[20]  # Use a different star
    civ3_params = CivilizationParams(
        id="civ_3",
        name="Conquerors",
        origin_star=star3,
        population=1.2e6,
        reproduction_rate=0.012,
        individual_lifespan=80,
        expansion_rate=0.06,
        expansion_range=90,
        cooperation_factor=0.2,  # Not cooperative
        aggression_factor=0.8,  # Aggressive
        founding_date=0,
        tech_level=0.9,
        tech_advancement_rate=0.004,
        time_horizon=500,
        biological_type="biological",
        organization_type="individual",
        motivation="resource",  # Focused on resources
    )
    civ3 = Civilization(civ3_params)
    universe.add_civilization(civ3)

    # Run the simulation for 200 steps
    print("Running simulation...")
    for step in range(200):
        universe.update()
        if step % 50 == 0:
            print(f"Step {step}, date: {universe.current_date}")

    print("\nSimulation complete!")
    print(f"Final date: {universe.current_date}")
    print(f"Active civilizations: {len(universe.civilizations)}")

    for civ_id, civ in universe.civilizations.items():
        print(
            f"{civ.params.name}: {len(civ.visited_stars)} stars, tech level {civ.params.tech_level:.2f}"
        )

    # Create visualizer
    visualizer = UniverseVisualizer(universe)

    # Plot the universe state
    fig1, _ = visualizer.plot_3d_state()

    # Plot various histories
    fig2, _ = visualizer.plot_population_history()
    fig3, _ = visualizer.plot_tech_history()
    fig4, _ = visualizer.plot_expansion_history()

    # Show all plots
    plt.show()


if __name__ == "__main__":
    main()
