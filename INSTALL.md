# Installation Guide

This guide will help you set up the environment for running the Interstellar Civilization Simulation.

## Requirements

- Python 3.7+
- pip (Python package installer)

## Installation Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd abm-civilization
   ```

2. Create a virtual environment (recommended):

   ```bash
   # Using venv
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation

After installation, you can run the simulation using one of the following:

1. Run the example script (simple simulation with 3 civilizations):

   ```bash
   python example.py
   ```

2. Run the main simulation with default parameters:

   ```bash
   python main.py
   ```

3. Run with custom parameters:
   ```bash
   python main.py --stars 2000 --civs 8 --steps 1000
   ```

## Command-line Arguments (main.py)

- `--stars`: Number of stars in the universe (default: 1000)
- `--civs`: Number of civilizations (default: 5)
- `--steps`: Number of simulation steps (default: 500)
- `--size`: Size of the universe cube (default: 1000.0)
- `--no-plots`: Don't show plots
- `--save-plots`: Save plots to files
