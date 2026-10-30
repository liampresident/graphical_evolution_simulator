"""
Graphical Evolution Simulator  (v2)

Single-file upgrade of the original NEA project.

Run with:   python Evolution_Simulator_v2.py
Needs:      pygame   (pip install pygame)       -- tkinter and sqlite3 ship with Python

Sections
  1. Constants and small helpers
  2. Password hashing
  3. Database  (every query is parameterised, so there is no SQL injection)
  4. Simulation objects (Plant, Meat, Cell) and the Simulation / pygame loop
  5. Tkinter user interface (one window, one screen at a time)
"""
import csv
import hashlib
import hmac
import math
import os
import random
import re
import secrets
import sqlite3
import uuid
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox

import pygame

# --------------------------------------------------------------------------
# 1. Constants and helpers
# --------------------------------------------------------------------------
DB_PATH = "Simulator.db"

TICKS_PER_DAY = 2000
TICKS_PER_HOUR = 83            # 2000 ticks is roughly 24 in-game hours
MAX_CELL_SIZE = 14

BIOME_COLOURS = {"N": (144, 238, 144),   # Normal  - light green
                 "W": (173, 216, 230),   # Water   - light blue
                 "F": (0, 100, 0),       # Forest  - dark green
                 "D": (211, 169, 108)}   # Desert  - sandy yellow
BIOME_NAMES = {"N": "Normal", "W": "Water", "F": "Forest", "D": "Desert"}
# How likely plants are to spawn in each biome type when a world is created
BIOME_PLANT_WEIGHT = {"N": 5, "W": 6, "F": 8, "D": 3}

WORLD_SIZES = {"Small": 400, "Medium": 600, "Large": 800}
SPEED_STEPS = [1, 2, 4, 8]     # simulation ticks per frame (UP / DOWN keys)

MIN_USERNAME = 2
MIN_PASSWORD = 6
MIN_RECOVERY = 6

GRAPH_TITLES = {"CellGraph": "Cell Count", "DietGraph": "Diet Average",
                "SizeGraph": "Size Average", "SpeedGraph": "Speed Average"}


def new_id():
    """Unique ID for worlds, cells and food."""
    return str(uuid.uuid4())


def clamp(value, low, high):
    return max(low, min(high, value))


def parse_history(text):
    """'0-5-6.5' -> [0.0, 5.0, 6.5]. Never uses eval()."""
    values = []
    for part in str(text).split("-"):
        try:
            values.append(float(part))
        except ValueError:
            pass
    return values


def format_history(values):
    # Fixed-point formatting: str(1e-05) would contain a '-' and corrupt the string
    return "-".join(f"{v:.4f}" for v in values)


# --------------------------------------------------------------------------
# 2. Password hashing (salted PBKDF2; old unsalted SHA-256 hashes still work
#    and are upgraded automatically the next time the user logs in)
# --------------------------------------------------------------------------
PBKDF2_ITERATIONS = 200_000


def normalise_word(word):
    return word.strip().lower()


def hash_secret(secret):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"),
                                 bytes.fromhex(salt), PBKDF2_ITERATIONS).hex()
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt}${digest}"


def is_modern_hash(stored):
    return bool(stored) and stored.startswith("pbkdf2$")


def verify_secret(secret, stored, legacy="sha256"):
    """legacy = 'sha256' for passwords, 'plain' for recovery words created by v1."""
    if not stored:
        return False
    if is_modern_hash(stored):
        try:
            _, iterations, salt, digest = stored.split("$")
            calc = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"),
                                       bytes.fromhex(salt), int(iterations)).hex()
        except ValueError:
            return False
        return hmac.compare_digest(calc.encode(), digest.encode())
    if legacy == "sha256":
        calc = hashlib.sha256(secret.encode("utf-8")).hexdigest()
        return hmac.compare_digest(calc.encode(), stored.encode())
    return hmac.compare_digest(normalise_word(secret).encode(),
                               normalise_word(stored).encode())


# --------------------------------------------------------------------------
# 3. Database
# --------------------------------------------------------------------------
class Database:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self._create_tables()

    def _create_tables(self):
        c = self.conn
        c.execute("""CREATE TABLE IF NOT EXISTS Users (
                        AccountID INTEGER PRIMARY KEY,
                        Username TEXT, Password TEXT, RecoveryWord TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS Simulations (
                        AccountID INTEGER, SimID TEXT PRIMARY KEY, SimName TEXT,
                        Day INTEGER, Status TEXT, WorldSize INTEGER, Biomes TEXT,
                        PopulationControl TEXT, MutationRate INTEGER,
                        BiomesPattern TEXT, Time INTEGER,
                        CellGraph TEXT, DietGraph TEXT, SpeedGraph TEXT, SizeGraph TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS Cells (
                        CellID TEXT PRIMARY KEY, SimID TEXT, Speed REAL, Size REAL,
                        Metabolism REAL, Fertility REAL, Diet REAL, Sight REAL,
                        Energy REAL, Position_x REAL, Position_y REAL,
                        Lifespan INTEGER, Angle REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS Foods (
                        FoodID TEXT PRIMARY KEY, SimID TEXT, Position_x REAL,
                        Position_y REAL, Size REAL, MorP TEXT)""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_cells_sim ON Cells(SimID)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_foods_sim ON Foods(SimID)")
        c.commit()

    # ---------------- accounts ----------------
    def username_taken(self, username, ignore_id=None):
        row = self.conn.execute("SELECT AccountID FROM Users WHERE Username = ?",
                                (username,)).fetchone()
        return row is not None and row[0] != ignore_id

    def create_user(self, username, password, recovery_word):
        """Returns the new AccountID, or None if the username is taken."""
        if self.username_taken(username):
            return None
        new_account = self.conn.execute(
            "SELECT COALESCE(MAX(AccountID), 0) + 1 FROM Users").fetchone()[0]
        self.conn.execute(
            "INSERT INTO Users(AccountID, Username, Password, RecoveryWord) VALUES(?,?,?,?)",
            (new_account, username, hash_secret(password),
             hash_secret(normalise_word(recovery_word))))
        self.conn.commit()
        return new_account

    def authenticate(self, username, password):
        row = self.conn.execute(
            "SELECT AccountID, Password FROM Users WHERE Username = ?", (username,)).fetchone()
        if row and verify_secret(password, row[1], "sha256"):
            if not is_modern_hash(row[1]):          # silently upgrade old hashes
                self.set_password(row[0], password)
            return row[0]
        return None

    def check_recovery(self, username, word):
        row = self.conn.execute(
            "SELECT AccountID, RecoveryWord FROM Users WHERE Username = ?", (username,)).fetchone()
        if row and verify_secret(normalise_word(word), row[1], "plain"):
            if not is_modern_hash(row[1]):
                self.conn.execute("UPDATE Users SET RecoveryWord = ? WHERE AccountID = ?",
                                  (hash_secret(normalise_word(word)), row[0]))
                self.conn.commit()
            return row[0]
        return None

    def set_password(self, account_id, password):
        self.conn.execute("UPDATE Users SET Password = ? WHERE AccountID = ?",
                          (hash_secret(password), account_id))
        self.conn.commit()

    def get_username(self, account_id):
        row = self.conn.execute("SELECT Username FROM Users WHERE AccountID = ?",
                                (account_id,)).fetchone()
        return row[0] if row else ""

    def update_user(self, account_id, username, password=None, recovery_word=None):
        """Blank password / recovery word means 'keep the current one'."""
        if self.username_taken(username, ignore_id=account_id):
            return "That username is already taken"
        self.conn.execute("UPDATE Users SET Username = ? WHERE AccountID = ?",
                          (username, account_id))
        if password:
            self.conn.execute("UPDATE Users SET Password = ? WHERE AccountID = ?",
                              (hash_secret(password), account_id))
        if recovery_word:
            self.conn.execute("UPDATE Users SET RecoveryWord = ? WHERE AccountID = ?",
                              (hash_secret(normalise_word(recovery_word)), account_id))
        self.conn.commit()
        return None

    def delete_user(self, account_id):
        for (sim_id,) in self.conn.execute(
                "SELECT SimID FROM Simulations WHERE AccountID = ?", (account_id,)).fetchall():
            self._delete_world_rows(sim_id)
        self.conn.execute("DELETE FROM Users WHERE AccountID = ?", (account_id,))
        self.conn.commit()

    def purge_guest(self):
        """Guest worlds (AccountID 0) can't be reloaded, so don't let them pile up."""
        for (sim_id,) in self.conn.execute(
                "SELECT SimID FROM Simulations WHERE AccountID = 0").fetchall():
            self._delete_world_rows(sim_id)
        self.conn.commit()

    # ---------------- worlds ----------------
    def _delete_world_rows(self, sim_id):
        for table in ("Cells", "Foods", "Simulations"):
            self.conn.execute(f"DELETE FROM {table} WHERE SimID = ?", (sim_id,))

    def delete_world(self, sim_id):
        self._delete_world_rows(sim_id)
        self.conn.commit()

    def list_worlds(self, account_id):
        return self.conn.execute(
            "SELECT SimID, SimName, Day FROM Simulations WHERE AccountID = ? ORDER BY SimName",
            (account_id,)).fetchall()

    def create_world(self, account_id, p):
        """p: dict of the options chosen on the New World screen. Returns the new SimID."""
        sim_id = new_id()
        ws = p["world_size"]
        if p["biomes"]:
            pattern = "".join(random.choice("NWFD") for _ in range(16))
        else:
            pattern = "N" * 16

        self.conn.execute(
            """INSERT INTO Simulations(AccountID, SimID, SimName, Day, Status, WorldSize, Biomes,
               PopulationControl, MutationRate, BiomesPattern, Time,
               CellGraph, DietGraph, SpeedGraph, SizeGraph)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (account_id, sim_id, p["name"], 0, "Alive", ws,
             "Yes" if p["biomes"] else "No", "Yes" if p["pop_control"] else "No",
             p["mutation"], pattern, 0, str(p["cells"]), "0", "0", "0"))

        cells = []
        for _ in range(p["cells"]):
            if p["genes"] == "random":
                size = random.randint(1, 10)
                speed = random.randint(0, 100) / 100
                sight = random.randint(0, 100)
                fertility = random.randint(1, 100)
                diet = random.randint(0, 100) / 100
            else:
                size = p["size"]
                speed = p["speed"] / 10
                sight = p["sight"]
                fertility = p["fertility"]
                diet = p["diet"] / 100
            metabolism = round(speed ** 2 / size, 2)
            cells.append((new_id(), sim_id, speed, size, metabolism, fertility, diet, sight,
                          5 * size, random.randint(0, ws), random.randint(0, ws), 0,
                          random.uniform(0, 2 * math.pi)))
        self.conn.executemany(
            """INSERT INTO Cells(CellID, SimID, Speed, Size, Metabolism, Fertility, Diet, Sight,
               Energy, Position_x, Position_y, Lifespan, Angle) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            cells)

        weights = [BIOME_PLANT_WEIGHT[pattern[i]] for i in range(16)]
        plants = []
        for _ in range(p["cells"] + 10):
            if p["biomes"]:
                block = random.choices(range(16), weights=weights)[0]
                q = ws / 4
                x = random.uniform((block % 4) * q, (block % 4 + 1) * q)
                y = random.uniform((block // 4) * q, (block // 4 + 1) * q)
            else:
                x = random.uniform(10, ws - 10)
                y = random.uniform(10, ws - 10)
            plants.append((new_id(), sim_id, x, y, random.randint(1, 5), "Plant"))
        self.conn.executemany(
            "INSERT INTO Foods(FoodID, SimID, Position_x, Position_y, Size, MorP) VALUES(?,?,?,?,?,?)",
            plants)
        self.conn.commit()
        return sim_id

    def load_world(self, sim_id):
        c = self.conn
        row = c.execute(
            """SELECT SimName, MutationRate, PopulationControl, WorldSize, BiomesPattern, Day, Time,
               CellGraph, DietGraph, SizeGraph, SpeedGraph FROM Simulations WHERE SimID = ?""",
            (sim_id,)).fetchone()
        if row is None:
            raise ValueError("World not found")
        return {
            "name": row[0], "mutation": int(row[1] or 0),
            "pop_control": row[2] == "Yes", "world_size": int(row[3]),
            "pattern": row[4] or "N" * 16, "day": int(row[5]), "hour": int(row[6]),
            "history": {"CellGraph": parse_history(row[7]), "DietGraph": parse_history(row[8]),
                        "SizeGraph": parse_history(row[9]), "SpeedGraph": parse_history(row[10])},
            "cells": c.execute(
                """SELECT CellID, Speed, Size, Position_x, Position_y, Sight, Energy, Diet,
                   Metabolism, Fertility, Angle, Lifespan FROM Cells WHERE SimID = ?""",
                (sim_id,)).fetchall(),
            "plants": c.execute(
                "SELECT FoodID, Position_x, Position_y, Size FROM Foods WHERE SimID = ? AND MorP = 'Plant'",
                (sim_id,)).fetchall(),
            "meat": c.execute(
                "SELECT FoodID, Position_x, Position_y, Size FROM Foods WHERE SimID = ? AND MorP = 'Meat'",
                (sim_id,)).fetchall(),
        }

    def save_world(self, sim):
        """Write the whole simulation state in a single transaction."""
        c = self.conn
        with c:
            c.execute("DELETE FROM Cells WHERE SimID = ?", (sim.sim_id,))
            c.execute("DELETE FROM Foods WHERE SimID = ?", (sim.sim_id,))
            c.executemany(
                """INSERT INTO Cells(CellID, SimID, Speed, Size, Metabolism, Fertility, Diet, Sight,
                   Energy, Position_x, Position_y, Lifespan, Angle) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [(k.cell_id, sim.sim_id, k.speed, k.size, k.metabolism, k.fertility, k.diet,
                  k.sight, k.energy, k.x, k.y, k.lifespan, k.angle) for k in sim.cells])
            foods = [(p.food_id, sim.sim_id, p.x, p.y, p.size, "Plant") for p in sim.plants]
            foods += [(m.food_id, sim.sim_id, m.x, m.y, m.size, "Meat") for m in sim.meat]
            c.executemany(
                "INSERT INTO Foods(FoodID, SimID, Position_x, Position_y, Size, MorP) VALUES(?,?,?,?,?,?)",
                foods)
            h = sim.history
            c.execute(
                """UPDATE Simulations SET Day = ?, Time = ?, CellGraph = ?, DietGraph = ?,
                   SizeGraph = ?, SpeedGraph = ? WHERE SimID = ?""",
                (sim.day, sim.sim_time // TICKS_PER_HOUR, format_history(h["CellGraph"]),
                 format_history(h["DietGraph"]), format_history(h["SizeGraph"]),
                 format_history(h["SpeedGraph"]), sim.sim_id))


# --------------------------------------------------------------------------
# 4. Simulation
# --------------------------------------------------------------------------
class Plant:
    def __init__(self, food_id, x, y, size, maturity=0):
        self.food_id = food_id
        self.x = x
        self.y = y
        self.size = size
        self.maturity = maturity
        self.eaten = False

    def update(self, sim):
        self.maturity += 1
        if self.maturity in (500, 1000) and self.size <= 10:
            self.size += 1
        if self.maturity >= 1000:
            self.maturity = 0
        # Spread a seed
        if self.maturity == 400 and len(sim.plants) + len(sim.new_plants) < sim.max_plants:
            nx = clamp(self.x + random.randint(-50, 50), 0, sim.world_size)
            ny = clamp(self.y + random.randint(-50, 50), 0, sim.world_size)
            sim.new_plants.append(Plant(new_id(), nx, ny, 1))


class Meat:
    def __init__(self, food_id, x, y, size, tick=0):
        self.food_id = food_id
        self.x = x
        self.y = y
        self.size = size
        self.tick = tick
        self.eaten = False

    def update(self):
        """Returns True once the meat has rotted away."""
        self.tick += 1
        if self.tick > 400:
            self.tick = 0
            self.size -= 1
        return self.size <= 1


class Cell:
    def __init__(self, cell_id, speed, size, x, y, sight, energy, diet,
                 metabolism, fertility, angle, lifespan):
        self.cell_id = cell_id
        self.speed = abs(speed)
        self.size = size
        self.x = x
        self.y = y
        self.sight = sight
        self.energy = energy
        self.diet = diet
        self.metabolism = metabolism
        self.fertility = fertility
        self.angle = angle
        self.lifespan = lifespan        # age in days
        self.biome = "Normal"
        self.dead = False

    def move(self, sim):
        ws = sim.world_size
        self.biome = sim.biome_at(self.x, self.y)

        # Head for the closest visible food, otherwise wander gently
        best = self.sight
        target = None
        for food in sim.plants + sim.meat:
            if food.eaten:
                continue
            d = math.hypot(food.x - self.x, food.y - self.y)
            if d <= best:
                best = d
                target = food
        if target is not None:
            self.angle = math.atan2(target.y - self.y, target.x - self.x)
        else:
            self.angle += random.uniform(-0.15, 0.15)

        step = self.speed * (0.5 if self.biome == "Water" else 1.0)   # water slows cells
        self.x += math.cos(self.angle) * step
        self.y += math.sin(self.angle) * step

        # Bounce off the world edge
        if self.x - self.size <= 0 or self.x + self.size >= ws:
            self.angle = math.pi - self.angle
            self.x = clamp(self.x, self.size + 1, ws - self.size - 1)
        if self.y - self.size <= 0 or self.y + self.size >= ws:
            self.angle = -self.angle
            self.y = clamp(self.y, self.size + 1, ws - self.size - 1)

    def eat(self, sim):
        reach2 = self.size ** 2
        for food in sim.plants:
            if not food.eaten and (self.x - food.x) ** 2 + (self.y - food.y) ** 2 < reach2:
                food.eaten = True
                self.energy += food.size * self.diet
        for food in sim.meat:
            if not food.eaten and (self.x - food.x) ** 2 + (self.y - food.y) ** 2 < reach2:
                food.eaten = True
                self.energy += food.size * self.diet

    def burn_energy(self):
        """Desert doubles the cost of living. Returns True if the cell starved."""
        self.energy -= self.metabolism * (1.0 if self.biome == "Desert" else 0.5)
        return self.energy <= 0

    def reproduce(self, sim):
        """Returns a mutated child, or None."""
        if self.energy < 30 or random.randint(0, 4000) > self.fertility:
            return None
        self.energy -= 10

        def mutate(value, low, high):
            return clamp(value * (1 + random.uniform(-sim.mutation, sim.mutation)), low, high)

        speed = mutate(self.speed, 0, 3)
        size = mutate(self.size, 1, MAX_CELL_SIZE)
        return Cell(new_id(), speed, size, self.x + 5, self.y,
                    mutate(self.sight, 0, 300), size * 9, mutate(self.diet, 0, 2),
                    round(speed ** 2 / size, 2), mutate(self.fertility, 1, 200),
                    self.angle + math.pi, 0)

    def colour(self):
        """Red channel fades with age, green with diet, blue with speed."""
        r = 255 - min(self.lifespan * 25, 200)
        g = 255 - int(min(self.diet, 1) * 220)
        b = 255 - int(min(self.speed / 2, 1) * 220)
        return (r, g, b)


class Simulation:
    def __init__(self, db, sim_id):
        self.db = db
        self.sim_id = sim_id
        data = db.load_world(sim_id)
        self.name = data["name"]
        self.mutation = data["mutation"] / 100
        self.pop_control = data["pop_control"]
        self.world_size = data["world_size"]
        self.pattern = data["pattern"]
        self.day = data["day"]
        self.sim_time = data["hour"] * TICKS_PER_HOUR
        self.history = data["history"]
        for key in self.history:                       # old worlds may have empty histories
            if not self.history[key]:
                self.history[key] = [0.0]

        self.cells = [Cell(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11])
                      for r in data["cells"]]
        self.plants = [Plant(r[0], r[1], r[2], r[3], random.randint(0, 300)) for r in data["plants"]]
        self.meat = [Meat(r[0], r[1], r[2], r[3]) for r in data["meat"]]
        self.new_plants = []

        self.max_cells = 30 if self.pop_control else 150
        self.max_plants = 45 if self.pop_control else 200

        # UI state (filled in by run())
        self.running = True
        self.mode = "run"            # run / paused / graph
        self.speed_idx = 0
        self.selected = None
        self.graph_key = "CellGraph"
        self.flash = ("", 0)

    # ---------------- world helpers ----------------
    def biome_at(self, x, y):
        q = self.world_size / 4
        col = int(clamp(x // q, 0, 3))
        row = int(clamp(y // q, 0, 3))
        index = row * 4 + col
        letter = self.pattern[index] if index < len(self.pattern) else "N"
        return BIOME_NAMES.get(letter, "Normal")

    # ---------------- one tick ----------------
    def step(self):
        self.sim_time += 1
        if self.sim_time >= TICKS_PER_DAY:
            self.new_day()
        if self.pop_control:
            self.population_control()

        self.new_plants = []
        babies = []
        for cell in self.cells:
            cell.move(self)
            cell.eat(self)
            if cell.burn_energy():
                cell.dead = True
                self.meat.append(Meat(new_id(), cell.x, cell.y, max(2.0, cell.size / 2)))
                continue
            if len(self.cells) + len(babies) < self.max_cells:
                child = cell.reproduce(self)
                if child:
                    babies.append(child)
        self.cells = [c for c in self.cells if not c.dead] + babies
        if self.selected is not None and self.selected.dead:
            self.selected = None

        self.plants = [p for p in self.plants if not p.eaten]
        for p in self.plants:
            p.update(self)
        self.plants += self.new_plants

        self.meat = [m for m in self.meat if not m.eaten and not m.update()]

    def population_control(self):
        ws = self.world_size
        if len(self.cells) < 2:
            speed = random.randint(0, 100) / 50
            size = random.randint(1, 10)
            self.cells.append(Cell(
                new_id(), speed, size, random.randint(0, ws), random.randint(0, ws),
                random.randint(0, 200), 5 * size, random.randint(0, 100) / 100,
                round(speed ** 2 / size, 2), random.randint(1, 100),
                random.uniform(0, 2 * math.pi), 0))
        if len(self.plants) < 4:
            self.plants.append(Plant(new_id(), random.randint(0, ws), random.randint(0, ws),
                                     random.randint(1, 5)))

    def new_day(self):
        self.day += 1
        self.sim_time = 0
        for c in self.cells:
            c.lifespan += 1
        n = len(self.cells)
        self.history["CellGraph"].append(n)
        self.history["DietGraph"].append(sum(c.diet for c in self.cells) / n if n else 0)
        self.history["SizeGraph"].append(sum(c.size for c in self.cells) / n if n else 0)
        self.history["SpeedGraph"].append(sum(c.speed for c in self.cells) / n if n else 0)
        self.db.save_world(self)                       # autosave once per day

    # ---------------- saving / exporting ----------------
    def save(self):
        self.db.save_world(self)

    def export_csv(self):
        safe = re.sub(r"[^\w\-]+", "_", self.name) or "world"
        path = os.path.abspath(f"{safe}_stats.csv")
        h = self.history
        rows = zip(range(len(h["CellGraph"])), h["CellGraph"], h["DietGraph"],
                   h["SizeGraph"], h["SpeedGraph"])
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Day", "Cell count", "Diet average", "Size average", "Speed average"])
            w.writerows(rows)
        return path

    def show_message(self, text, seconds=2.5):
        self.flash = (text, pygame.time.get_ticks() + int(seconds * 1000))

    # ---------------- pygame main loop ----------------
    def run(self):
        pygame.init()
        ws = self.world_size
        self.screen = pygame.display.set_mode((ws, ws))
        pygame.display.set_caption(f"Evolution Simulator - {self.name}")
        self.font = pygame.font.SysFont(None, 22)
        self.small = pygame.font.SysFont(None, 18)
        self.big = pygame.font.SysFont(None, 32)
        self.night = pygame.Surface((ws, ws))
        self.night.fill((10, 10, 50))
        self.pause_rect = pygame.Rect(10, 10, 36, 36)
        self._build_menu()
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if self.mode == "run":
                for _ in range(SPEED_STEPS[self.speed_idx]):
                    self.step()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self.save()
        pygame.quit()

    # ---------------- input ----------------
    def _build_menu(self):
        ws = self.world_size
        panel = pygame.Rect(0, 0, 260, 330)
        panel.center = (ws // 2, ws // 2)
        self.menu_panel = panel
        x, y = panel.x + 20, panel.y + 50
        w, h = 220, 28
        half = 105
        self.menu = [
            ("Resume", pygame.Rect(x, y, w, h), self.resume),
            ("Save now", pygame.Rect(x, y + 36, w, h), self.manual_save),
            ("Export stats (CSV)", pygame.Rect(x, y + 72, w, h), self.do_export),
            ("Cell count", pygame.Rect(x, y + 124, half, h), lambda: self.open_graph("CellGraph")),
            ("Diet", pygame.Rect(x + 115, y + 124, half, h), lambda: self.open_graph("DietGraph")),
            ("Size", pygame.Rect(x, y + 160, half, h), lambda: self.open_graph("SizeGraph")),
            ("Speed", pygame.Rect(x + 115, y + 160, half, h), lambda: self.open_graph("SpeedGraph")),
            ("Save & quit", pygame.Rect(x, y + 212, w, h), self.quit_sim),
        ]
        self.graph_panel = pygame.Rect(30, 30, ws - 60, ws - 60)
        self.graph_back = pygame.Rect(self.graph_panel.right - 90, self.graph_panel.y + 8, 80, 26)

    def resume(self):
        self.mode = "run"

    def manual_save(self):
        self.save()
        self.show_message("World saved")

    def do_export(self):
        try:
            self.show_message(f"Saved {os.path.basename(self.export_csv())}", 4)
        except OSError as exc:
            self.show_message(f"Export failed: {exc}", 4)

    def open_graph(self, key):
        self.graph_key = key
        self.mode = "graph"

    def quit_sim(self):
        self.running = False

    def handle_event(self, e):
        if e.type == pygame.QUIT:
            self.running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                self.mode = "paused" if self.mode == "run" else "run"
            elif e.key == pygame.K_ESCAPE:
                self.mode = "paused" if self.mode == "run" else ("paused" if self.mode == "graph" else "run")
            elif e.key == pygame.K_UP:
                self.speed_idx = min(self.speed_idx + 1, len(SPEED_STEPS) - 1)
            elif e.key == pygame.K_DOWN:
                self.speed_idx = max(self.speed_idx - 1, 0)
            elif e.key == pygame.K_s:
                self.manual_save()
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.click(e.pos)

    def click(self, pos):
        if self.mode == "run":
            if self.pause_rect.collidepoint(pos):
                self.mode = "paused"
                return
            best, best_d = None, None
            for c in self.cells:
                d = math.hypot(pos[0] - c.x, pos[1] - c.y)
                if d <= max(8, 1.5 * c.size) and (best_d is None or d < best_d):
                    best, best_d = c, d
            self.selected = best
        elif self.mode == "paused":
            for _, rect, action in self.menu:
                if rect.collidepoint(pos):
                    action()
                    return
        elif self.mode == "graph":
            if self.graph_back.collidepoint(pos):
                self.mode = "paused"

    # ---------------- drawing ----------------
    def text(self, string, pos, font=None, colour=(0, 0, 0)):
        self.screen.blit((font or self.font).render(string, True, colour), pos)

    def draw(self):
        ws = self.world_size
        scr = self.screen
        q = ws / 4
        for i in range(16):
            letter = self.pattern[i] if i < len(self.pattern) else "N"
            pygame.draw.rect(scr, BIOME_COLOURS[letter],
                             pygame.Rect((i % 4) * q, (i // 4) * q, q + 1, q + 1))

        for p in self.plants:
            pygame.draw.circle(scr, (0, 200, 0), (int(p.x), int(p.y)), max(1, int(p.size)))
        for m in self.meat:
            pygame.draw.circle(scr, (139, 0, 0), (int(m.x), int(m.y)), max(1, int(m.size)))
        for c in self.cells:
            pygame.draw.circle(scr, c.colour(), (int(c.x), int(c.y)), max(1, int(c.size)))
        if self.selected is not None:
            pygame.draw.circle(scr, (255, 255, 0), (int(self.selected.x), int(self.selected.y)),
                               int(self.selected.size) + 4, 2)

        # Day / night
        hour = (self.sim_time // TICKS_PER_HOUR) % 24
        if hour < 6 or hour >= 20:
            alpha = 90
        elif hour < 8 or hour >= 18:
            alpha = 40
        else:
            alpha = 0
        if alpha:
            self.night.set_alpha(alpha)
            scr.blit(self.night, (0, 0))

        self.draw_hud(hour)
        if self.selected is not None and self.mode == "run":
            self.draw_inspector()
        if self.mode == "paused":
            self.draw_menu()
        elif self.mode == "graph":
            self.draw_graph()

        text, until = self.flash
        if text and pygame.time.get_ticks() < until:
            surf = self.font.render(text, True, (255, 255, 255))
            box = surf.get_rect(center=(ws // 2, ws - 20)).inflate(20, 10)
            pygame.draw.rect(scr, (30, 30, 30), box, border_radius=6)
            scr.blit(surf, surf.get_rect(center=box.center))

    def draw_hud(self, hour):
        scr = self.screen
        pygame.draw.rect(scr, (255, 255, 255), self.pause_rect)
        if self.mode == "run":
            pygame.draw.line(scr, (0, 0, 0), (21, 20), (21, 36), 5)
            pygame.draw.line(scr, (0, 0, 0), (35, 20), (35, 36), 5)
        else:
            pygame.draw.polygon(scr, (0, 0, 0), [(21, 18), (21, 38), (38, 28)])
        h12 = hour % 12 or 12
        clock_text = f"{h12}:00 {'pm' if hour >= 12 else 'am'}"
        width = min(self.world_size - 66, 360)
        pygame.draw.rect(scr, (255, 255, 255), pygame.Rect(56, 10, width, 36))
        self.text(f"Day {self.day}   {clock_text}   Cells {len(self.cells)}   Plants {len(self.plants)}",
                  (62, 13))
        self.text(f"Speed x{SPEED_STEPS[self.speed_idx]}  |  Space pause, Up/Down speed, S save",
                  (62, 30), self.small, (80, 80, 80))

    def draw_inspector(self):
        c = self.selected
        lines = [f"Speed: {c.speed:.2f}", f"Size: {c.size:.1f}", f"Energy: {c.energy:.1f}",
                 f"Sight: {c.sight:.0f}", f"Diet: {c.diet:.2f}", f"Fertility: {c.fertility:.0f}",
                 f"Age (days): {c.lifespan}", f"Biome: {c.biome}"]
        box = pygame.Rect(10, self.world_size - 20 - 18 * len(lines), 150, 12 + 18 * len(lines))
        pygame.draw.rect(self.screen, (255, 255, 255), box)
        pygame.draw.rect(self.screen, (0, 0, 0), box, 1)
        for i, line in enumerate(lines):
            self.text(line, (box.x + 8, box.y + 6 + 18 * i), self.small)

    def draw_menu(self):
        scr = self.screen
        pygame.draw.rect(scr, (255, 255, 255), self.menu_panel)
        pygame.draw.rect(scr, (0, 0, 0), self.menu_panel, 2)
        self.text("PAUSED", (self.menu_panel.x + 90, self.menu_panel.y + 15), self.big)
        self.text("Graphs", (self.menu_panel.x + 20, self.menu_panel.y + 50 + 104), self.small, (80, 80, 80))
        for label, rect, _ in self.menu:
            pygame.draw.rect(scr, (235, 235, 235), rect)
            pygame.draw.rect(scr, (0, 0, 0), rect, 1)
            surf = self.font.render(label, True, (0, 0, 0))
            scr.blit(surf, surf.get_rect(center=rect.center))

    def draw_graph(self):
        scr = self.screen
        panel = self.graph_panel
        pygame.draw.rect(scr, (255, 255, 255), panel)
        pygame.draw.rect(scr, (0, 0, 0), panel, 2)
        self.text(GRAPH_TITLES[self.graph_key], (panel.x + 12, panel.y + 12), self.big)
        pygame.draw.rect(scr, (235, 235, 235), self.graph_back)
        pygame.draw.rect(scr, (0, 0, 0), self.graph_back, 1)
        surf = self.font.render("Back", True, (0, 0, 0))
        scr.blit(surf, surf.get_rect(center=self.graph_back.center))

        data = self.history[self.graph_key]
        if len(data) < 2:
            self.text("Not enough data yet - let a full day pass.", (panel.x + 12, panel.y + 60))
            return
        left, right = panel.x + 60, panel.right - 20
        top, bottom = panel.y + 60, panel.bottom - 40
        lo, hi = min(data), max(data)
        if hi == lo:
            hi, lo = hi + 1, lo - 1
        pts = [(left + i / (len(data) - 1) * (right - left),
                bottom - (v - lo) / (hi - lo) * (bottom - top)) for i, v in enumerate(data)]
        pygame.draw.line(scr, (0, 0, 0), (left, top), (left, bottom), 2)
        pygame.draw.line(scr, (0, 0, 0), (left, bottom), (right, bottom), 2)
        pygame.draw.lines(scr, (30, 100, 200), False, pts, 2)
        self.text(f"{hi:.2f}", (panel.x + 8, top - 6), self.small)
        self.text(f"{lo:.2f}", (panel.x + 8, bottom - 8), self.small)
        self.text("Day 0", (left, bottom + 8), self.small)
        self.text(f"Day {len(data) - 1}", (right - 40, bottom + 8), self.small)


# --------------------------------------------------------------------------
# 5. User interface (one Tk window, screens are swapped in and out)
# --------------------------------------------------------------------------
class App:
    def __init__(self, db_path=DB_PATH):
        self.db = Database(db_path)
        self.account_id = 0
        self.root = tk.Tk()
        self.root.title("Graphical Evolution Simulator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.f10 = tkFont.Font(family="Times", size=10)
        self.f12 = tkFont.Font(family="Times", size=12)
        self.f28 = tkFont.Font(family="Times", size=28)
        self.f7 = tkFont.Font(family="Times", size=7)
        self.frame = None
        self.show_main_menu()

    def run(self):
        self.root.mainloop()

    # ---------------- helpers ----------------
    def switch(self, builder, *args):
        if self.frame is not None:
            self.frame.destroy()
        self.root.unbind("<Return>")
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)
        builder(self.frame, *args)

    def title(self, f, text, y=60):
        tk.Label(f, font=self.f28, text=text).place(relx=0.5, y=y, anchor="n")

    def button(self, f, text, command, x, y, w=100, h=30, font=None):
        b = tk.Button(f, text=text, command=command, font=font or self.f10)
        b.place(x=x, y=y, width=w, height=h)
        return b

    def entry(self, f, label, x, y, hidden=False, gap=130):
        tk.Label(f, text=label, font=self.f10).place(x=x, y=y)
        e = tk.Entry(f, show="*" if hidden else "", width=24)
        e.place(x=x + gap, y=y)
        return e

    def error_label(self, f, y):
        lab = tk.Label(f, text="", fg="red", font=self.f10)
        lab.place(relx=0.5, y=y, anchor="n")
        return lab

    def quit(self):
        if self.account_id == 0:
            self.db.purge_guest()
        self.db.conn.close()
        self.root.destroy()

    # ---------------- start screens ----------------
    def show_main_menu(self):
        self.account_id = 0
        self.switch(self.build_main_menu)

    def build_main_menu(self, f):
        self.title(f, "Graphical Evolution\nSimulator", 60)
        self.button(f, "Log In", self.show_login, 250, 200, 100, 40)
        self.button(f, "Sign Up", self.show_signup, 250, 250, 100, 40)
        self.button(f, "Continue as Guest", self.start_guest, 250, 300, 100, 24, self.f7)
        self.button(f, "Quit", self.quit, 510, 10, 70, 25)

    def start_guest(self):
        self.account_id = 0
        self.show_home()

    # ---------------- log in ----------------
    def show_login(self):
        self.switch(self.build_login)

    def build_login(self, f):
        self.title(f, "Log In", 60)
        user = self.entry(f, "Username", 100, 200)
        pw = self.entry(f, "Password", 100, 250, hidden=True)
        err = self.error_label(f, 360)

        def submit(_event=None):
            username, password = user.get().strip(), pw.get()
            if len(username) < MIN_USERNAME or len(password) < MIN_PASSWORD:
                err.config(text="Username or password too short")
                return
            account = self.db.authenticate(username, password)
            if account is None:
                err.config(text="Login failed")
                return
            self.account_id = account
            self.show_home()

        def clear():
            user.delete(0, tk.END)
            pw.delete(0, tk.END)

        self.root.bind("<Return>", submit)
        self.button(f, "Log In", submit, 100, 310)
        self.button(f, "Clear", clear, 250, 310)
        self.button(f, "Forgotten Password?", self.show_recovery, 400, 310, 130)
        self.button(f, "Back", self.show_main_menu, 10, 10, 70)

    def show_recovery(self):
        self.switch(self.build_recovery)

    def build_recovery(self, f):
        self.title(f, "Account Recovery", 60)
        user = self.entry(f, "Username", 100, 200)
        word = self.entry(f, "Memorable word", 100, 250)
        err = self.error_label(f, 360)

        def submit(_event=None):
            account = self.db.check_recovery(user.get().strip(), word.get())
            if account is None:
                err.config(text="No account found")
            else:
                self.switch(self.build_new_password, account)

        self.root.bind("<Return>", submit)
        self.button(f, "Submit", submit, 100, 310)
        self.button(f, "Back", self.show_login, 10, 10, 70)

    def build_new_password(self, f, account):
        self.title(f, "Set New Password", 60)
        p1 = self.entry(f, "Password", 100, 200, hidden=True)
        p2 = self.entry(f, "Re-enter", 100, 250, hidden=True)
        err = self.error_label(f, 360)

        def submit(_event=None):
            if len(p1.get()) < MIN_PASSWORD:
                err.config(text=f"Password needs at least {MIN_PASSWORD} characters")
            elif p1.get() != p2.get():
                err.config(text="Passwords do not match")
            else:
                self.db.set_password(account, p1.get())
                messagebox.showinfo("Password updated", "You can now log in with your new password.")
                self.show_login()

        self.root.bind("<Return>", submit)
        self.button(f, "Submit", submit, 100, 310)

    # ---------------- sign up ----------------
    def show_signup(self):
        self.switch(self.build_signup)

    def build_signup(self, f):
        self.title(f, "Sign Up", 60)
        user = self.entry(f, "Username", 50, 200)
        pw = self.entry(f, "Password", 50, 250, hidden=True)
        word = self.entry(f, "Memorable word", 50, 300)
        tk.Label(f, font=self.f10, justify="left",
                 text="A word such as a pet name,\nused to recover your account\nif you forget your password").place(x=370, y=285)
        err = self.error_label(f, 400)

        def submit(_event=None):
            username = user.get().strip()
            if len(username) < MIN_USERNAME:
                err.config(text=f"Username needs at least {MIN_USERNAME} characters")
            elif len(pw.get()) < MIN_PASSWORD:
                err.config(text=f"Password needs at least {MIN_PASSWORD} characters")
            elif len(word.get().strip()) < MIN_RECOVERY:
                err.config(text=f"Memorable word needs at least {MIN_RECOVERY} characters")
            else:
                account = self.db.create_user(username, pw.get(), word.get())
                if account is None:
                    err.config(text="An account with this username already exists")
                else:
                    self.account_id = account
                    self.show_home()

        def clear():
            for e in (user, pw, word):
                e.delete(0, tk.END)

        self.root.bind("<Return>", submit)
        self.button(f, "Sign up", submit, 100, 350)
        self.button(f, "Clear", clear, 250, 350)
        self.button(f, "Back", self.show_main_menu, 10, 10, 70)

    # ---------------- home ----------------
    def show_home(self):
        self.switch(self.build_home)

    def build_home(self, f):
        self.title(f, "Graphical Evolution\nSimulator", 50)
        who = "Guest" if self.account_id == 0 else f"{self.db.get_username(self.account_id)} (ID {self.account_id})"
        tk.Label(f, font=self.f10, text=f"Account: {who}").place(x=10, y=10)
        self.button(f, "New", self.show_new_world, 50, 240, 90, 30)
        if self.account_id != 0:
            self.button(f, "Load", self.show_load_world, 50, 280, 90, 30)
            self.button(f, "Account", self.show_account, 50, 320, 90, 30)
        self.button(f, "Log Off", self.log_off, 400, 10, 80, 28)
        self.button(f, "Quit", self.quit, 500, 10, 80, 28)

    def log_off(self):
        if self.account_id == 0:
            self.db.purge_guest()
        self.show_main_menu()

    def launch(self, sim_id):
        """Hide the Tk window, run the pygame simulation, then come back to the home screen."""
        error = None
        self.root.withdraw()
        try:
            Simulation(self.db, sim_id).run()
        except Exception as exc:                              # keep the app alive on any crash
            error = exc
            if pygame.get_init():
                pygame.quit()
        self.root.deiconify()
        if error is not None:
            messagebox.showerror("Simulation error", f"The simulation stopped unexpectedly:\n{error}")
        self.show_home()

    # ---------------- new world ----------------
    def show_new_world(self):
        self.switch(self.build_new_world)

    def build_new_world(self, f):
        defaults = {"speed": 5, "size": 5, "fertility": 50, "sight": 50, "diet": 50}
        scale_defs = [("speed", "Speed", 0, 10), ("size", "Size", 1, 10),
                      ("fertility", "Fertility", 0, 100), ("sight", "Sight depth", 0, 100),
                      ("diet", "Diet scale", 0, 100)]

        tk.Label(f, text="Create New World", font=self.f12).place(x=20, y=15)
        tk.Label(f, text="World name:").place(x=20, y=55)
        name = tk.Entry(f, width=18)
        name.place(x=110, y=55)

        tk.Label(f, text="Starting cells:").place(x=320, y=40)
        cells = tk.Scale(f, from_=1, to=20, length=130, orient="horizontal")
        cells.set(8)
        cells.place(x=430, y=22)
        tk.Label(f, text="Mutation %:").place(x=320, y=80)
        mutation = tk.Scale(f, from_=0, to=100, length=130, orient="horizontal")
        mutation.set(10)
        mutation.place(x=430, y=62)

        genes = tk.StringVar(value="uniform")
        tk.Radiobutton(f, text="Uniform genes", variable=genes, value="uniform",
                       command=lambda: toggle()).place(x=20, y=110)
        tk.Radiobutton(f, text="Random genes", variable=genes, value="random",
                       command=lambda: toggle()).place(x=180, y=110)

        scales = {}
        for i, (key, label, lo, hi) in enumerate(scale_defs):
            col, row = i % 2, i // 2
            x = 20 + col * 290
            y = 145 + row * 50
            tk.Label(f, text=label + ":").place(x=x, y=y + 18)
            s = tk.Scale(f, from_=lo, to=hi, length=150, orient="horizontal")
            s.set(defaults[key])
            s.place(x=x + 90, y=y)
            scales[key] = s

        def toggle():
            random_mode = genes.get() == "random"
            for s in scales.values():
                s.config(state="disabled" if random_mode else "normal",
                         bg="grey" if random_mode else f.cget("bg"))

        def reset():
            for key, s in scales.items():
                s.set(defaults[key])

        bio = tk.IntVar()
        pop = tk.IntVar()
        tk.Checkbutton(f, text="Biomes", variable=bio).place(x=20, y=305)
        tk.Checkbutton(f, text="Population control", variable=pop).place(x=120, y=305)

        tk.Label(f, text="World size:").place(x=20, y=340)
        size_var = tk.StringVar(value="Small")
        for i, label in enumerate(WORLD_SIZES):
            tk.Radiobutton(f, text=label, variable=size_var, value=label).place(x=100 + i * 90, y=338)

        err = self.error_label(f, 380)

        def info():
            messagebox.showinfo("Settings help",
                "Uniform: every cell starts with the same stats.\n"
                "Random: every cell starts with random stats.\n\n"
                "Speed: how fast they move\nSize: how big they are\n"
                "Sight: how far a cell can see food\nFertility: how often a cell reproduces\n"
                "Diet: how much energy a cell gets from food\n\n"
                "Mutation %: how much a child's stats can differ from its parent's.\n"
                "Biomes: water slows cells, deserts burn energy faster.\n"
                "Population control: respawns cells and plants if they run low, and caps numbers.\n\n"
                "In the simulation: click a cell to inspect it, Space pauses, Up/Down changes speed.")

        def start():
            world_name = name.get().strip()
            if not world_name:
                err.config(text="Enter a name for the world")
                return
            if len(world_name) > 30:
                err.config(text="World name must be 30 characters or fewer")
                return
            params = {"name": world_name, "cells": cells.get(), "mutation": mutation.get(),
                      "genes": genes.get(), "biomes": bool(bio.get()), "pop_control": bool(pop.get()),
                      "world_size": WORLD_SIZES[size_var.get()]}
            for key, s in scales.items():
                params[key] = s.get()
            self.launch(self.db.create_world(self.account_id, params))

        self.button(f, "Start", start, 20, 420, 90)
        self.button(f, "Reset", reset, 120, 420, 90)
        self.button(f, "Info", info, 220, 420, 90)
        self.button(f, "Back", self.show_home, 320, 420, 90)

    # ---------------- load world ----------------
    def show_load_world(self):
        self.switch(self.build_load_world)

    def build_load_world(self, f):
        tk.Label(f, text="Select a world:", font=self.f12).place(x=40, y=40)
        worlds = self.db.list_worlds(self.account_id)
        ids = [w[0] for w in worlds]

        frame = tk.Frame(f)
        frame.place(x=40, y=80)
        scroll = tk.Scrollbar(frame)
        box = tk.Listbox(frame, yscrollcommand=scroll.set, selectmode="single", width=45, height=12)
        scroll.config(command=box.yview)
        box.pack(side="left")
        scroll.pack(side="right", fill="y")
        for _, sim_name, day in worlds:
            box.insert(tk.END, f"{sim_name}   (day {day})")
        err = self.error_label(f, 350)
        if not worlds:
            err.config(text="You have no saved worlds yet", fg="black")

        def chosen():
            sel = box.curselection()
            if not sel:
                err.config(text="Select a world first", fg="red")
                return None
            return ids[sel[0]]

        def start():
            sim_id = chosen()
            if sim_id:
                self.launch(sim_id)

        def delete():
            sel = box.curselection()
            sim_id = chosen()
            if sim_id and messagebox.askyesno("Delete world", "Delete this world permanently?"):
                self.db.delete_world(sim_id)
                ids.pop(sel[0])
                box.delete(sel[0])

        self.button(f, "Start", start, 40, 320, 90)
        self.button(f, "Delete", delete, 140, 320, 90)
        self.button(f, "Back", self.show_home, 10, 10, 70)

    # ---------------- account ----------------
    def show_account(self):
        self.switch(self.build_account)

    def build_account(self, f):
        self.title(f, "Account Settings", 40)
        user = self.entry(f, "Username", 80, 170, gap=170)
        user.insert(0, self.db.get_username(self.account_id))
        pw = self.entry(f, "New password", 80, 210, hidden=True, gap=170)
        word = self.entry(f, "New memorable word", 80, 250, gap=170)
        tk.Label(f, font=self.f7, text="Leave password / memorable word blank to keep them as they are").place(x=80, y=280)
        err = self.error_label(f, 380)

        def update():
            username = user.get().strip()
            if len(username) < MIN_USERNAME:
                err.config(text=f"Username needs at least {MIN_USERNAME} characters", fg="red")
            elif pw.get() and len(pw.get()) < MIN_PASSWORD:
                err.config(text=f"Password needs at least {MIN_PASSWORD} characters", fg="red")
            elif word.get().strip() and len(word.get().strip()) < MIN_RECOVERY:
                err.config(text=f"Memorable word needs at least {MIN_RECOVERY} characters", fg="red")
            else:
                problem = self.db.update_user(self.account_id, username, pw.get(), word.get().strip())
                if problem:
                    err.config(text=problem, fg="red")
                else:
                    pw.delete(0, tk.END)
                    word.delete(0, tk.END)
                    err.config(text="Account updated", fg="green")

        def delete():
            if messagebox.askyesno("Delete account",
                                   "This permanently deletes your account and all your worlds. Continue?"):
                self.db.delete_user(self.account_id)
                self.show_main_menu()

        self.button(f, "Update", update, 80, 320)
        self.button(f, "Delete Account", delete, 200, 320, 120)
        self.button(f, "Back", self.show_home, 10, 10, 70)


if __name__ == "__main__":
    App().run()
