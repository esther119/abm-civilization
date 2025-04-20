#!/usr/bin/env python3
"""
Interstellar Civilization Simulation

This script runs a simulation of civilizations expanding across star systems.
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import argparse

from models import Universe, Civilization, CivilizationParams
from simulation import UniverseVisualizer


def create_civilization(universe, id_num, name, star, **params):
    """
    Helper function to create a civilization with default parameters.

    Args:
        universe: Universe object
        id_num: ID number for the civilization
        name: Name of the civilization
        star: Origin star
        **params: Optional parameter overrides

    Returns:
        Civilization object
    """
    # Default parameters
    default_params = {
        "population": 1e6,
        "reproduction_rate": 0.01,
        "individual_lifespan": 100,
        "expansion_rate": 0.05,
        "expansion_range": 100,
        "cooperation_factor": 0.5,
        "aggression_factor": 0.5,
        "founding_date": universe.current_date,
        "tech_level": 1.0,
        "tech_advancement_rate": 0.005,
        "time_horizon": 1000,
        "biological_type": "biological",
        "organization_type": "individual",
        "motivation": "expansion",
    }

    # Override defaults with provided params
    for key, value in params.items():
        default_params[key] = value

    # Create the civilization parameters
    civ_params = CivilizationParams(
        id=f"civ_{id_num}", name=name, origin_star=star, **default_params
    )

    # Create and return the civilization
    return Civilization(civ_params)


def run_simulation(
    num_stars=1000,
    num_civs=5,
    sim_steps=500,
    universe_size=1000.0,
    show_plots=True,
    save_plots=False,
):
    """
    Run the simulation with specified parameters.

    Args:
        num_stars: Number of stars in the universe
        num_civs: Number of civilizations to create
        sim_steps: Number of simulation steps to run
        universe_size: Size of the universe cube
        show_plots: Whether to display plots
        save_plots: Whether to save plots to files
    """
    print(f"Initializing universe with {num_stars} stars...")
    universe = Universe(size=universe_size)
    universe.initialize_stars(num_stars)

    print("Creating civilizations...")

    # Motivation types with equal probability
    motivation_types = ["expansion", "knowledge", "seeding", "resource"]
    # Organization types with equal probability
    organization_types = ["individual", "hive", "singular"]
    # Biological types with equal probability
    biological_types = ["biological", "artificial", "hybrid"]

    # Civilization names (could be more creative in a real implementation)
    names = [f"Civilization {i+1}" for i in range(num_civs)]

    # Create civilizations with different parameters
    for i in range(num_civs):
        # Pick a random star with good resources for the origin
        candidate_stars = sorted(
            universe.get_all_stars(), key=lambda s: s.resources, reverse=True
        )[
            :20
        ]  # Top 20 stars by resources
        origin_star = random.choice(candidate_stars)

        # Create civilization with random parameters
        civ = create_civilization(
            universe,
            i + 1,
            names[i],
            origin_star,
            # Random parameters
            reproduction_rate=random.uniform(0.005, 0.015),
            individual_lifespan=random.uniform(80, 120),
            expansion_rate=random.uniform(0.03, 0.08),
            expansion_range=random.uniform(80, 120),
            cooperation_factor=random.uniform(0.3, 0.7),
            aggression_factor=random.uniform(0.3, 0.7),
            tech_level=random.uniform(0.8, 1.2),
            tech_advancement_rate=random.uniform(0.003, 0.008),
            time_horizon=random.uniform(500, 1500),
            biological_type=random.choice(biological_types),
            organization_type=random.choice(organization_types),
            motivation=random.choice(motivation_types),
        )

        # Add to universe
        universe.add_civilization(civ)

    print(f"Running simulation for {sim_steps} steps...")
    # Run simulation with progress bar
    for _ in tqdm(range(sim_steps)):
        universe.update()

    print("\nSimulation complete!")
    print(f"Final date: {universe.current_date}")
    print(f"Active civilizations: {len(universe.civilizations)}")

    # Create visualizer
    visualizer = UniverseVisualizer(universe)

    if show_plots or save_plots:
        # Plot 3D state
        fig1, _ = visualizer.plot_3d_state()
        if save_plots:
            fig1.savefig("universe_3d_state.png", dpi=300)

        # Plot population history
        fig2, _ = visualizer.plot_population_history()
        if save_plots:
            fig2.savefig("population_history.png", dpi=300)

        # Plot technology history
        fig3, _ = visualizer.plot_tech_history()
        if save_plots:
            fig3.savefig("tech_history.png", dpi=300)

        # Plot expansion history
        fig4, _ = visualizer.plot_expansion_history()
        if save_plots:
            fig4.savefig("expansion_history.png", dpi=300)

        # Plot universe statistics
        fig5 = visualizer.plot_universe_statistics()
        if fig5 is not None and save_plots:
            fig5.savefig("universe_statistics.png", dpi=300)

        if show_plots:
            plt.show()

    return universe, visualizer


def main():
    """Main function to parse arguments and run the simulation"""
    parser = argparse.ArgumentParser(description="Interstellar Civilization Simulation")
    parser.add_argument(
        "--stars", type=int, default=1000, help="Number of stars in the universe"
    )
    parser.add_argument("--civs", type=int, default=5, help="Number of civilizations")
    parser.add_argument(
        "--steps", type=int, default=500, help="Number of simulation steps"
    )
    parser.add_argument(
        "--size", type=float, default=1000.0, help="Size of the universe cube"
    )
    parser.add_argument("--no-plots", action="store_true", help="Don't show plots")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to files")

    args = parser.parse_args()

    # Run the simulation
    run_simulation(
        num_stars=args.stars,
        num_civs=args.civs,
        sim_steps=args.steps,
        universe_size=args.size,
        show_plots=not args.no_plots,
        save_plots=args.save_plots,
    )


if __name__ == "__main__":
    main()
