#!/usr/bin/env python3
"""
Detailed Interstellar Civilization Simulation

This script runs a simulation with detailed output every 10 steps.
It shows the progress of each civilization over time.
"""

import numpy as np
import matplotlib.pyplot as plt
from models import Universe, Civilization, CivilizationParams
from simulation import UniverseVisualizer
from tabulate import tabulate  # Make sure to install: pip install tabulate


def print_detailed_stats(universe, step):
    """Print detailed statistics about all civilizations"""
    print(f"\n======== STEP {step} (Date: {universe.current_date}) ========")

    # Prepare data for tabulation
    headers = [
        "Civilization",
        "Stars",
        "Population",
        "Tech Level",
        "Type",
        "Motivation",
    ]
    rows = []

    # Total universe stats
    total_stars = len(universe.stars)
    inhabited_stars = set()
    for civ in universe.civilizations.values():
        inhabited_stars.update(civ.visited_stars.keys())

    print(
        f"Universe: {len(inhabited_stars)}/{total_stars} stars inhabited ({len(inhabited_stars)/total_stars*100:.1f}%)"
    )

    # Per-civilization stats
    for civ_id, civ in universe.civilizations.items():
        # Get civilization details
        name = civ.params.name
        num_stars = len(civ.visited_stars)
        population = civ.get_total_population()
        tech_level = civ.params.tech_level
        bio_type = civ.params.biological_type
        org_type = civ.params.organization_type
        motivation = civ.params.motivation

        # Add to table
        rows.append(
            [
                name,
                num_stars,
                f"{population:.1e}",
                f"{tech_level:.2f}",
                f"{bio_type}/{org_type}",
                motivation,
            ]
        )

    # Print table
    print(tabulate(rows, headers, tablefmt="grid"))

    # Recent events
    print("\nRecent events:")
    event_count = 0
    for civ in universe.civilizations.values():
        # Get the 2 most recent events for each civilization
        recent_events = civ.history[-2:] if len(civ.history) >= 2 else civ.history
        for event in recent_events:
            event_count += 1
            date = event["date"]
            event_type = event["event"]
            civ_name = civ.params.name

            # Format event details based on type
            details = ""
            if event_type == "expansion":
                from_star = event["data"].get("from_star", "unknown")
                to_star = event["data"].get("to_star", "unknown")
                details = f"expanded from star_{from_star[-1:]} to star_{to_star[-1:]}"
            elif event_type == "tech_exchange":
                with_civ = event["data"].get("with_civilization", "unknown")
                boost = event["data"].get("tech_boost", 0)
                details = f"gained {boost:.3f} tech from {with_civ}"
            elif event_type == "conflict_won" or event_type == "conflict_lost":
                against = event["data"].get("against_civilization", "unknown")
                at_star = event["data"].get("at_star", "unknown")
                details = f"{event_type} against {against} at star_{at_star[-1:]}"

            print(f"  [{date:.0f}] {civ_name}: {event_type} - {details}")

            # Limit to 6 total events to avoid too much output
            if event_count >= 6:
                break
        if event_count >= 6:
            break

    print("\n")


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

    # Print initial state
    print("\n=== SIMULATION START ===")
    print_detailed_stats(universe, 0)

    # Run the simulation for 200 steps
    print("Running simulation with detailed output every 10 steps...")
    total_steps = 200

    for step in range(1, total_steps + 1):
        universe.update()

        # Print detailed stats every 10 steps
        if step % 10 == 0:
            print_detailed_stats(universe, step)

    print("\n=== SIMULATION COMPLETE ===")
    print(f"Final date: {universe.current_date}")
    print(f"Active civilizations: {len(universe.civilizations)}")

    # Print final summary
    for civ_id, civ in universe.civilizations.items():
        colony_count = len(civ.colonies)
        max_pop_colony = max(civ.colonies.values()) if civ.colonies else 0
        total_pop = civ.get_total_population()

        print(f"\n{civ.params.name}:")
        print(f"  Stars visited: {len(civ.visited_stars)}")
        print(f"  Active colonies: {colony_count}")
        print(f"  Technology level: {civ.params.tech_level:.2f}")
        print(f"  Total population: {total_pop:.1e}")
        print(f"  Largest colony: {max_pop_colony:.1e}")

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
