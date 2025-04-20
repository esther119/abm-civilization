import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd


# Helper function to convert matplotlib colors to hex format
def color_to_hex(color):
    """Convert matplotlib color to hex string"""
    if isinstance(color, str):
        return color

    if isinstance(color, tuple) or isinstance(color, np.ndarray):
        # Convert RGB(A) to hex
        if len(color) >= 3:
            r, g, b = color[:3]
            r = min(max(int(r * 255), 0), 255)
            g = min(max(int(g * 255), 0), 255)
            b = min(max(int(b * 255), 0), 255)
            return f"#{r:02x}{g:02x}{b:02x}"

    return "#000000"  # Default to black if conversion fails


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

        # Collect civilization data for parameters text box
        civ_params_text = "Initial Civilization Parameters:\n"
        civ_params_text += "--------------------------------\n"

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

            # Add civilization parameters to the text box
            civ_params_text += f"\n{civ.params.name} ({color_to_hex(color)}):\n"
            civ_params_text += (
                f"  Type: {civ.params.biological_type}/{civ.params.organization_type}\n"
            )
            civ_params_text += f"  Motivation: {civ.params.motivation}\n"
            civ_params_text += f"  Tech: {civ.params.tech_level:.2f} (growth rate: {civ.params.tech_advancement_rate:.4f})\n"
            civ_params_text += f"  Expansion rate: {civ.params.expansion_rate:.2f}\n"
            civ_params_text += f"  Cooperation/Aggression: {civ.params.cooperation_factor:.2f}/{civ.params.aggression_factor:.2f}\n"

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

        # Add the parameters text box if show_labels is True
        if show_labels:
            # Add a text box with civilization parameters in the bottom right
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            fig.text(
                0.95,
                0.05,
                civ_params_text,
                fontsize=8,
                verticalalignment="bottom",
                horizontalalignment="right",
                bbox=props,
                transform=fig.transFigure,
            )

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
            # Get the actual visit dates for each star from the visited_stars dictionary
            visit_dates = sorted(
                [(date, star_id) for star_id, date in civ.visited_stars.items()]
            )

            if not visit_dates:
                continue

            # Create timeline of cumulative unique stars
            dates = [d for d, _ in visit_dates]
            # Count unique stars at each date point (always adding 1 for each new star)
            cumulative_counts = range(1, len(visit_dates) + 1)

            ax.plot(
                dates,
                cumulative_counts,
                label=f"{civ.params.name} ({len(civ.visited_stars)} stars)",
                color=self.colors[i % len(self.colors)],
            )

        ax.set_xlabel("Time")
        ax.set_ylabel("Number of Unique Stars")
        ax.set_title("Civilization Expansion History (Unique Stars)")
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

        # Calculate percentage of inhabited stars
        total_stars = len(self.universe.stars)
        star_percentages = [count / total_stars * 100 for count in star_counts]

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
        axs[2].plot(dates, star_counts, label=f"Count (Total: {total_stars})")
        ax2 = axs[2].twinx()
        ax2.plot(dates, star_percentages, "r--", label="Percentage")
        ax2.set_ylabel("Percentage (%)")
        ax2.set_ylim(0, 100)

        axs[2].set_title("Inhabited Stars")
        axs[2].set_ylabel("Count")
        axs[2].set_xlabel("Time")
        axs[2].grid(True)

        # Combine legends
        lines1, labels1 = axs[2].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        axs[2].legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.tight_layout()
        return fig
