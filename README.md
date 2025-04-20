# Interstellar Civilization Simulation

An agent-based model simulating the interaction of civilizations across star systems.

## Features

- Models expansion of multiple civilizations across star systems
- Simulates population growth, technological advancement, and interactions
- Configurable parameters for different civilization types
- 3D visualization of civilization expansion

## How It Works

### Core Components

#### 1. Star Systems

- Represented by the `Star` class
- Have 3D coordinates, resource levels (0-1), and planets
- Resources affect population capacity and growth rates
- Track which civilizations have visited them

#### 2. Civilizations

- Defined by parameters including:
  - **Population**: Size, reproduction rate, lifespan
  - **Technology**: Level, advancement rate
  - **Expansion**: Rate, range
  - **Interaction**: Cooperation vs. aggression factors
  - **Type**: Biological/artificial/hybrid, individual/hive/singular organization
  - **Motivation**: Expansion, knowledge, seeding, or resource acquisition

#### 3. Universe

- Contains and manages all stars and civilizations
- Handles time progression and interactions
- Maintains global statistics and history

### Simulation Flow

1. **Initialization**:

   - Generate stars with random positions and resource levels
   - Create civilizations with different parameters
   - Place each civilization at its origin star

2. **Each Time Step**:

   - Update population of each colony based on reproduction rates and resources
   - Advance technology levels (faster for knowledge-focused civilizations)
   - Attempt expansion to new stars based on probability calculations
   - Process interactions between civilizations at shared locations

3. **Interactions**:
   - **Peaceful**: When cooperation > aggression, civilizations share technology
   - **Hostile**: When aggression > cooperation, they compete for control
   - Combat outcomes depend on population, tech level, and aggression factors
   - Civilizations can be eliminated if they lose all colonies

### Civilization Types

The example script showcases three distinct types:

1. **Explorers**: Expansion-focused, cooperative

   - Spread rapidly to many systems
   - Biological individuals

2. **Scholars**: Knowledge-focused, highly cooperative

   - Advance technology quickly
   - Expand slowly but develop powerful tech advantages
   - Hybrid species with hive mind organization

3. **Conquerors**: Resource-focused, aggressive
   - Target resource-rich stars
   - More likely to engage in conflicts
   - Biological individuals with short-term planning

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd abm-civilization

# Install dependencies
pip install -r requirements.txt
```

## Usage

You can run the simulation in two ways:

```bash
# Run example with three predefined civilization types
python example.py

# Run the main simulation with customizable parameters
python main.py

# Run with custom parameters
python main.py --stars 2000 --civs 8 --steps 1000
```

### Command-line Options

- `--stars`: Number of stars in the universe (default: 1000)
- `--civs`: Number of civilizations (default: 5)
- `--steps`: Number of simulation steps (default: 500)
- `--size`: Size of the universe cube (default: 1000.0)
- `--no-plots`: Don't show plots
- `--save-plots`: Save plots to files

## Parameters

- **Population**: Growth rate, initial size, lifespan
- **Expansion**: Rate, range
- **Interaction**: Cooperation factor, aggression factor
- **Technology**: Advancement rate, initial level
- **Civilization Traits**: Time horizon, biological type, organization type, motivation

## Visualization

After running, the simulation generates several visualizations:

- 3D plot showing stars and civilization territories
- Population growth charts for each civilization
- Technology advancement histories
- Expansion timelines showing colonization rates
