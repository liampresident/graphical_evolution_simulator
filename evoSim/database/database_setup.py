"""
Initialise the SQLite database used by evoSimV1.py.

Run from the project root:
    python database/database_setup.py

The database is created at the project root as Simulator.db.
Existing tables and data are not deleted or overwritten.
"""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "Simulator.db"


def create_database():
    """Create the four tables expected by evoSimV1.py if they do not exist."""
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                AccountID INTEGER UNIQUE,
                Username TEXT,
                Password TEXT,
                RecoveryWord INTEGER,
                PRIMARY KEY (AccountID)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Simulations (
                AccountID INTEGER,
                SimID INTEGER,
                SimName TEXT,
                Day INTEGER,
                Status TEXT,
                WorldSize TEXT,
                Biomes TEXT,
                PopulationControl TEXT,
                MutationRate REAL,
                BiomesPattern STRING,
                Time INTEGER,
                CellGraph STRING,
                DietGraph STRING,
                SpeedGraph STRING,
                SizeGraph STRING,
                PRIMARY KEY (AccountID, SimID)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Cells (
                CellID INTEGER UNIQUE,
                SimID INTEGER,
                Speed REAL,
                Size INTEGER,
                Metabolism REAL,
                Fertility INTEGER,
                Diet INTEGER,
                Sight INTEGER,
                Energy REAL,
                Position_x REAL,
                Position_y REAL,
                Lifespan INTEGER,
                Angle REAL,
                PRIMARY KEY (CellID, SimID)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Foods (
                FoodID INTEGER,
                SimID INTEGER,
                Position_x REAL,
                Position_y REAL,
                Size INTEGER,
                MorP TEXT,
                PRIMARY KEY (FoodID, SimID)
            )
        """)

        connection.commit()
        print(f"Database ready: {DATABASE_PATH}")
        print("Tables available: Users, Simulations, Cells, Foods")

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
