#!/usr/bin/env python3
"""
Interstellar Civilization Simulation with Exportable Reports

This script runs a simulation and saves detailed reports to files
for easy sharing with others.
"""

import numpy as np
import matplotlib.pyplot as plt
from models import Universe, Civilization, CivilizationParams
from simulation import UniverseVisualizer
from tabulate import tabulate
import os
import time
from datetime import datetime


class SimulationReporter:
    """Class to handle reporting and exporting simulation data"""

    def __init__(self, output_dir="simulation_reports"):
        """Initialize the reporter with an output directory"""
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Set up file paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir
        self.base_filename = f"{output_dir}/sim_report_{timestamp}"
        self.html_file = f"{self.base_filename}.html"
        self.txt_file = f"{self.base_filename}.txt"
        self.summary_file = f"{self.base_filename}_summary.txt"

        # Initialize HTML file with header
        with open(self.html_file, "w") as f:
            f.write(
                """<!DOCTYPE html>
<html>
<head>
    <title>Interstellar Civilization Simulation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        h1, h2, h3 { color: #2c3e50; }
        .step { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .events { margin-left: 20px; }
        .event { margin-bottom: 5px; }
        .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Interstellar Civilization Simulation Report</h1>
    <p>Generated on: """
                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + """</p>
    <div class="summary">
        <h2>Simulation Parameters</h2>
        <ul>
            <li>Universe Size: 500.0</li>
            <li>Stars: 300</li>
            <li>Simulation Steps: 200</li>
            <li>Civilizations: 3 (Explorers, Scholars, Conquerors)</li>
        </ul>
    </div>
"""
            )

        # Initialize text file with header
        with open(self.txt_file, "w") as f:
            f.write(f"INTERSTELLAR CIVILIZATION SIMULATION REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"SIMULATION PARAMETERS\n")
            f.write(f"Universe Size: 500.0\n")
            f.write(f"Stars: 300\n")
            f.write(f"Simulation Steps: 200\n")
            f.write(f"Civilizations: 3 (Explorers, Scholars, Conquerors)\n\n")

        print(f"Simulation reports will be saved to:")
        print(f"- HTML Report: {self.html_file}")
        print(f"- Text Report: {self.txt_file}")
        print(f"- Summary: {self.summary_file}")

    def add_step_report(self, universe, step):
        """Add a report for the current simulation step"""
        # Prepare data
        headers = [
            "Civilization",
            "Stars",
            "Population",
            "Tech Level",
            "Type",
            "Motivation",
        ]
        rows = []

        # Universe stats
        total_stars = len(universe.stars)
        inhabited_stars = set()
        for civ in universe.civilizations.values():
            inhabited_stars.update(civ.visited_stars.keys())

        universe_summary = f"Universe: {len(inhabited_stars)}/{total_stars} stars inhabited ({len(inhabited_stars)/total_stars*100:.1f}%)"

        # Civilization stats
        for civ_id, civ in universe.civilizations.items():
            name = civ.params.name
            num_stars = len(civ.visited_stars)
            population = civ.get_total_population()
            tech_level = civ.params.tech_level
            bio_type = civ.params.biological_type
            org_type = civ.params.organization_type
            motivation = civ.params.motivation

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

        # Extract recent events
        events = []
        for civ in universe.civilizations.values():
            recent_events = civ.history[-2:] if len(civ.history) >= 2 else civ.history
            for event in recent_events:
                date = event["date"]
                event_type = event["event"]
                civ_name = civ.params.name

                # Format event details
                details = ""
                if event_type == "expansion":
                    from_star = event["data"].get("from_star", "unknown")
                    to_star = event["data"].get("to_star", "unknown")
                    details = (
                        f"expanded from star_{from_star[-1:]} to star_{to_star[-1:]}"
                    )
                elif event_type == "tech_exchange":
                    with_civ = event["data"].get("with_civilization", "unknown")
                    boost = event["data"].get("tech_boost", 0)
                    details = f"gained {boost:.3f} tech from {with_civ}"
                elif event_type == "conflict_won" or event_type == "conflict_lost":
                    against = event["data"].get("against_civilization", "unknown")
                    at_star = event["data"].get("at_star", "unknown")
                    details = f"{event_type} against {against} at star_{at_star[-1:]}"

                events.append(
                    {
                        "date": date,
                        "civ_name": civ_name,
                        "event_type": event_type,
                        "details": details,
                    }
                )

        # Sort events by date (most recent first)
        events.sort(key=lambda x: x["date"], reverse=True)
        events = events[:6]  # Limit to 6 most recent events

        # Add to HTML file
        with open(self.html_file, "a") as f:
            f.write(
                f"""
    <div class="step">
        <h2>Step {step} (Date: {universe.current_date})</h2>
        <p>{universe_summary}</p>
        
        <h3>Civilization Status</h3>
        <table>
            <tr>
"""
            )
            # Write headers
            for header in headers:
                f.write(f"                <th>{header}</th>\n")
            f.write("            </tr>\n")

            # Write rows
            for row in rows:
                f.write("            <tr>\n")
                for cell in row:
                    f.write(f"                <td>{cell}</td>\n")
                f.write("            </tr>\n")

            f.write(
                """        </table>
        
        <h3>Recent Events</h3>
        <div class="events">
"""
            )

            # Write events
            for event in events:
                f.write(
                    f'            <div class="event">[{event["date"]:.0f}] {event["civ_name"]}: {event["event_type"]} - {event["details"]}</div>\n'
                )

            f.write(
                """        </div>
    </div>
"""
            )

        # Add to text file
        with open(self.txt_file, "a") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"STEP {step} (Date: {universe.current_date})\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"{universe_summary}\n\n")

            f.write("CIVILIZATION STATUS:\n")
            f.write(tabulate(rows, headers, tablefmt="grid"))
            f.write("\n\nRECENT EVENTS:\n")

            for event in events:
                f.write(
                    f'[{event["date"]:.0f}] {event["civ_name"]}: {event["event_type"]} - {event["details"]}\n'
                )

            f.write("\n")

    def add_final_summary(self, universe):
        """Add a final summary of the simulation"""
        # Create summary text
        summary = []
        summary.append(f"SIMULATION COMPLETE")
        summary.append(f"Final date: {universe.current_date}")
        summary.append(f"Active civilizations: {len(universe.civilizations)}")
        summary.append("")

        # Add details for each civilization
        for civ_id, civ in universe.civilizations.items():
            colony_count = len(civ.colonies)
            max_pop_colony = max(civ.colonies.values()) if civ.colonies else 0
            total_pop = civ.get_total_population()
            tech_growth = civ.params.tech_level / 1.0  # Compared to starting level

            summary.append(f"{civ.params.name}:")
            summary.append(f"  Stars visited: {len(civ.visited_stars)}")
            summary.append(f"  Active colonies: {colony_count}")
            summary.append(
                f"  Technology level: {civ.params.tech_level:.2f} ({tech_growth:.1f}x growth)"
            )
            summary.append(f"  Total population: {total_pop:.1e}")
            summary.append(f"  Largest colony: {max_pop_colony:.1e}")
            summary.append("")

        # Add to HTML file
        with open(self.html_file, "a") as f:
            f.write(
                """
    <div class="summary">
        <h2>Final Results</h2>
"""
            )
            for line in summary:
                if line.endswith(":"):
                    f.write(f"        <h3>{line[:-1]}</h3>\n")
                elif line == "":
                    f.write("        <br>\n")
                else:
                    f.write(f"        <p>{line}</p>\n")

            f.write(
                """    </div>
</body>
</html>
"""
            )

        # Add to text file
        with open(self.txt_file, "a") as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write("FINAL RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(summary))

        # Create a separate summary file
        with open(self.summary_file, "w") as f:
            f.write("INTERSTELLAR CIVILIZATION SIMULATION - SUMMARY\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n".join(summary))

    def save_visualizations(self, universe, visualizer):
        """Save visualizations as image files"""
        # Create visualization directory
        vis_dir = f"{self.output_dir}/visualizations"
        if not os.path.exists(vis_dir):
            os.makedirs(vis_dir)

        # Save 3D state
        fig1, _ = visualizer.plot_3d_state()
        fig1.savefig(f"{vis_dir}/universe_3d_state.png", dpi=300)

        # Save population history
        fig2, _ = visualizer.plot_population_history()
        fig2.savefig(f"{vis_dir}/population_history.png", dpi=300)

        # Save technology history
        fig3, _ = visualizer.plot_tech_history()
        fig3.savefig(f"{vis_dir}/tech_history.png", dpi=300)

        # Save expansion history
        fig4, _ = visualizer.plot_expansion_history()
        fig4.savefig(f"{vis_dir}/expansion_history.png", dpi=300)

        # Add links to HTML report
        with open(self.html_file, "a") as f:
            f.write(
                """
    <div class="visualizations">
        <h2>Visualizations</h2>
        <p>These visualizations show the simulation results:</p>
        <ul>
            <li><a href="visualizations/universe_3d_state.png">3D Universe State</a></li>
            <li><a href="visualizations/population_history.png">Population History</a></li>
            <li><a href="visualizations/tech_history.png">Technology History</a></li>
            <li><a href="visualizations/expansion_history.png">Expansion History</a></li>
        </ul>
    </div>
"""
            )

        print(f"Visualizations saved to {vis_dir}/")

        # Return figures for display
        return [fig1, fig2, fig3, fig4]


def main():
    # Initialize reporter
    reporter = SimulationReporter()

    # Create a universe with a smaller number of stars
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

    # Add initial state to report
    reporter.add_step_report(universe, 0)

    # Run the simulation
    print("Running simulation with reports every 10 steps...")
    total_steps = 200

    for step in range(1, total_steps + 1):
        universe.update()

        # Add report every 10 steps
        if step % 10 == 0:
            print(f"Processing step {step}/{total_steps}...")
            reporter.add_step_report(universe, step)

    # Add final summary
    print("Creating final summary...")
    reporter.add_final_summary(universe)

    # Create visualizer and save visualizations
    print("Generating and saving visualizations...")
    visualizer = UniverseVisualizer(universe)
    figures = reporter.save_visualizations(universe, visualizer)

    print("\nSimulation report complete!")
    print(f"HTML Report: {reporter.html_file}")
    print(f"Text Report: {reporter.txt_file}")
    print(f"Summary: {reporter.summary_file}")

    # Display visualizations
    plt.show()


if __name__ == "__main__":
    main()
