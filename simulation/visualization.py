import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd


class UniverseVisualizer:
    """
    Visualization tools for the universe simulation.

    This class provides methods to visualize the state of the universe,
    including 3D plots of stars and civilizations, population graphs,
    technology level graphs, and animations of expansion over time.
    """

    def __init__(self, universe):
        """
        Initialize the visualizer.

        Args:
            universe: The Universe object to visualize
        """
        self.universe = universe
        self.colors = plt.cm.tab10.colors  # Color cycle for civilizations

    def plot_3d_state(self, ax=None, fig=None, show_labels=True, highlight_civs=None):
        """
        Plot the current state of the universe in 3D.

        Args:
            ax: Optional matplotlib 3D axis to plot on
            fig: Optional matplotlib figure
            show_labels: Whether to show civilization labels
            highlight_civs: List of civilization IDs to highlight

        Returns:
            fig, ax: The figure and axis objects
        """
        if ax is None:
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection="3d")

        # Plot stars as small points
        positions = np.array([star.position for star in self.universe.stars.values()])
        resources = np.array([star.resources for star in self.universe.stars.values()])

        # Plot all stars as small points
        ax.scatter(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            c="lightgray",
            s=1,
            alpha=0.5,
        )

        # Plot civilizations
        for i, civ in enumerate(self.universe.civilizations.values()):
            # Get positions of stars visited by this civilization
            civ_stars = [
                self.universe.stars[star_id] for star_id in civ.visited_stars.keys()
            ]
            if not civ_stars:
                continue

            civ_positions = np.array([star.position for star in civ_stars])
            pop_sizes = np.array([civ.colonies.get(star.id, 0) for star in civ_stars])
            if pop_sizes.max() > 0:
                sizes = 10 + 40 * (pop_sizes / pop_sizes.max())
            else:
                sizes = 10

            # Color based on civilization
            color = self.colors[i % len(self.colors)]

            # Highlight if requested
            alpha = 1.0
            highlight = False
            if highlight_civs is not None:
                if civ.params.id not in highlight_civs:
                    alpha = 0.3
                else:
                    highlight = True

            # Plot colonies
            scatter = ax.scatter(
                civ_positions[:, 0],
                civ_positions[:, 1],
                civ_positions[:, 2],
                s=sizes,
                c=[color],
                alpha=alpha,
                label=civ.params.name,
            )

            # Highlight the civilization's home star
            origin_star = civ.params.origin_star
            ax.scatter(
                origin_star.position[0],
                origin_star.position[1],
                origin_star.position[2],
                s=100,
                c=[color],
                marker="*",
                alpha=alpha,
                edgecolor="white",
            )

            # Add a text label near the origin star only for highlighted civs
            if show_labels and (highlight_civs is None or highlight):
                ax.text(
                    origin_star.position[0],
                    origin_star.position[1],
                    origin_star.position[2],
                    civ.params.name,
                    color=color,
                    fontsize=8,
                )

        # Set limits and labels
        max_range = self.universe.size / 2
        ax.set_xlim(-max_range, max_range)
        ax.set_ylim(-max_range, max_range)
        ax.set_zlim(-max_range, max_range)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        ax.set_title(f"Universe at time {self.universe.current_date:.0f}")

        if show_labels:
            plt.legend(loc="upper right")

        return fig, ax

    def plot_population_history(self):
        """
        Plot population history for all civilizations over time.

        Returns:
            fig, ax: The figure and axis objects
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, civ in enumerate(self.universe.civilizations.values()):
            history = civ.population_history
            if not history:
                continue

            dates, populations = zip(*history)
            ax.plot(
                dates,
                populations,
                label=civ.params.name,
                color=self.colors[i % len(self.colors)],
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Population")
        ax.set_title("Civilization Population History")
        ax.set_yscale("log")
        ax.grid(True)
        plt.legend()

        return fig, ax

    def plot_tech_history(self):
        """
        Plot technology history for all civilizations over time.

        Returns:
            fig, ax: The figure and axis objects
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, civ in enumerate(self.universe.civilizations.values()):
            history = civ.tech_history
            if not history:
                continue

            dates, tech_levels = zip(*history)
            ax.plot(
                dates,
                tech_levels,
                label=civ.params.name,
                color=self.colors[i % len(self.colors)],
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Technology Level")
        ax.set_title("Civilization Technology History")
        ax.grid(True)
        plt.legend()

        return fig, ax

    def plot_expansion_history(self):
        """
        Plot the number of stars colonized by each civilization over time.

        Returns:
            fig, ax: The figure and axis objects
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, civ in enumerate(self.universe.civilizations.values()):
            # Extract expansion events from history
            events = [(e["date"], 1) for e in civ.history if e["event"] == "expansion"]
            events.insert(
                0, (civ.params.founding_date, 1)
            )  # Add founding date with 1 star

            # Convert to cumulative count
            dates, counts = zip(*events)
            cumulative_counts = np.cumsum(counts)

            ax.plot(
                dates,
                cumulative_counts,
                label=civ.params.name,
                color=self.colors[i % len(self.colors)],
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Number of Stars")
        ax.set_title("Civilization Expansion History")
        ax.grid(True)
        plt.legend()

        return fig, ax

    def create_expansion_animation(self, steps=100, interval=200):
        """
        Create an animation of the expansion of civilizations.

        Args:
            steps: Number of frames in the animation
            interval: Interval between frames in milliseconds

        Returns:
            animation: FuncAnimation object
        """
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Initialize with empty plot
        self.plot_3d_state(ax=ax, fig=fig)

        # Update function for animation
        def update(frame):
            ax.clear()
            # Copy the universe
            temp_universe = self.universe
            # Set the date to the appropriate frame
            temp_universe.current_date = frame
            # Plot the state at this date
            self.plot_3d_state(ax=ax, fig=fig, show_labels=False)
            ax.set_title(f"Universe at time {frame}")
            return (ax,)

        # Create animation
        max_date = self.universe.current_date
        frames = np.linspace(0, max_date, steps)
        animation = FuncAnimation(
            fig, update, frames=frames, interval=interval, blit=False
        )

        return animation

    def plot_civilization_stats(self, civ_id):
        """
        Plot detailed statistics for a specific civilization.

        Args:
            civ_id: ID of the civilization to analyze

        Returns:
            fig: The figure with multiple subplots
        """
        civ = self.universe.get_civilization(civ_id)
        if civ is None:
            raise ValueError(f"Civilization with ID {civ_id} not found")

        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Population history
        if civ.population_history:
            dates, populations = zip(*civ.population_history)
            axs[0, 0].plot(dates, populations)
            axs[0, 0].set_title(f"{civ.params.name} - Population History")
            axs[0, 0].set_xlabel("Time")
            axs[0, 0].set_ylabel("Population")
            axs[0, 0].set_yscale("log")
            axs[0, 0].grid(True)

        # Technology history
        if civ.tech_history:
            dates, tech_levels = zip(*civ.tech_history)
            axs[0, 1].plot(dates, tech_levels)
            axs[0, 1].set_title(f"{civ.params.name} - Technology History")
            axs[0, 1].set_xlabel("Time")
            axs[0, 1].set_ylabel("Technology Level")
            axs[0, 1].grid(True)

        # Expansion events
        expansion_events = [
            (e["date"], e["data"]["to_star"])
            for e in civ.history
            if e["event"] == "expansion"
        ]
        if expansion_events:
            dates, _ = zip(*expansion_events)
            axs[1, 0].hist(dates, bins=20)
            axs[1, 0].set_title(f"{civ.params.name} - Expansion Timeline")
            axs[1, 0].set_xlabel("Time")
            axs[1, 0].set_ylabel("Number of Expansions")
            axs[1, 0].grid(True)

        # Event counts
        event_types = [e["event"] for e in civ.history]
        if event_types:
            event_counts = pd.Series(event_types).value_counts()
            event_counts.plot(kind="bar", ax=axs[1, 1])
            axs[1, 1].set_title(f"{civ.params.name} - Event Types")
            axs[1, 1].set_xlabel("Event Type")
            axs[1, 1].set_ylabel("Count")

        plt.tight_layout()
        return fig

    def plot_universe_statistics(self):
        """
        Plot overall universe statistics over time.

        Returns:
            fig: The figure with multiple subplots
        """
        stats_events = [e for e in self.universe.history if e["event"] == "statistics"]
        if not stats_events:
            return None

        # Extract data
        dates = [e["date"] for e in stats_events]
        civ_counts = [e["data"]["civilizations"] for e in stats_events]
        pop_counts = [e["data"]["total_population"] for e in stats_events]
        star_counts = [e["data"]["inhabited_stars"] for e in stats_events]

        fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

        # Civilization count
        axs[0].plot(dates, civ_counts)
        axs[0].set_title("Number of Civilizations")
        axs[0].set_ylabel("Count")
        axs[0].grid(True)

        # Total population
        axs[1].plot(dates, pop_counts)
        axs[1].set_title("Total Population")
        axs[1].set_ylabel("Population")
        axs[1].set_yscale("log")
        axs[1].grid(True)

        # Inhabited stars
        axs[2].plot(dates, star_counts)
        axs[2].set_title("Inhabited Stars")
        axs[2].set_ylabel("Count")
        axs[2].set_xlabel("Time")
        axs[2].grid(True)

        plt.tight_layout()
        return fig
