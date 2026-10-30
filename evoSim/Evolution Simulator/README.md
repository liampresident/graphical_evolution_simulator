# Graphical Evolution Simulator

A Python-based artificial life simulator developed as my A-Level Computer Science NEA project.

The application creates a virtual ecosystem in which independently controlled organisms interact with their environment, search for food, reproduce and evolve over successive generations.

Built using Python, Pygame, Tkinter and SQLite, the project combines graphical simulation, object-oriented programming, database management and basic evolutionary concepts.

## Features

### Ecosystem Simulation
- Autonomous cells navigate the environment and search for nearby food.
- Organisms have individual characteristics, including speed, size, sight, fertility, diet and metabolism.
- Cells consume plants and other organisms to maintain their energy.
- Organisms reproduce when sufficient energy is available, passing characteristics to their offspring.
- Random mutations introduce variations in inherited characteristics.
- Plants grow and reproduce, while remains of deceased organisms gradually decay.

### Environmental Systems
- Four biome types: Normal, Water, Forest and Desert.
- Worlds are divided into a 4×4 biome grid.
- Environmental conditions influence organism movement and energy consumption.
- Plant distribution varies according to biome type.

### World Creation and Management
- Create worlds with configurable population sizes and world dimensions.
- Choose between uniform and randomly generated starting characteristics.
- Adjust mutation rates and enable optional population control.
- Save, load and delete existing simulations.
- SQLite database integration for storing simulation data.

### User Interface and Statistics
- Graphical interface built with Tkinter.
- Real-time simulation rendering using Pygame.
- Pause and resume simulation functionality.
- Inspect individual organisms and their characteristics.
- Generate graphs tracking population count, average diet, size and speed over simulated days.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pygame | Real-time graphical simulation |
| Tkinter | User interface and menus |
| SQLite | Account and simulation data persistence |
| Matplotlib | Statistical graphs |
| UUID | Unique identifiers for simulation objects |

## Running the Project

### Requirements

- Python 3
- Pygame
- Matplotlib
- Tkinter (usually included with standard Python installations)
- SQLite3 (included with standard Python installations)

### Installation

Install the external dependencies:

```bash
pip install pygame matplotlib
```

### Launching

Once the required SQLite database has been initialised with the expected tables, run:

```bash
python evoSimV1.py
```

**Database note:** The application expects a `Simulator.db` database containing the `Users`, `Simulations`, `Cells` and `Foods` tables. A clean database initialisation script is needed for a fresh installation.

## Project Background

This project was originally developed as part of my A-Level Computer Science coursework.

Development involved progressing from early prototypes towards a more complete application, introducing increasingly complex simulation behaviour, environmental interactions, account management and persistent data storage.

The final coursework implementation is preserved in `evoSimV1.py`.

An additional AI-assisted redevelopment was explored separately in `evoSimV2.py`. This version is not the original coursework submission and is kept distinct from the final original implementation.

## Future Improvements

- Refactor the application into separate modules and classes.
- Improve database security and use parameterised SQL queries throughout.
- Introduce more advanced genetic inheritance and evolutionary mechanics.
- Improve simulation performance with larger populations.
- Add more detailed statistical analysis and visualisation.
- Add Neural networks to the cells
