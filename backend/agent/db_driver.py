import sqlite3
import logging
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int

class DatabaseDriver:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        logger.info("Initializing DatabaseDriver with path: %s", db_path)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        logger.info("Opening database connection to: %s", self.db_path)
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            logger.info("Closing database connection")
            conn.close()

    def _init_db(self):
        logger.info("Initializing database tables")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create cars table
            logger.info("Creating cars table if not exists")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    vin TEXT PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            """)
            conn.commit()
            logger.info("Database initialization completed")

    def create_car(self, vin: str, make: str, model: str, year: int) -> Car:
        logger.info("Creating new car - VIN: %s, Make: %s, Model: %s, Year: %d", vin, make, model, year)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cars (vin, make, model, year) VALUES (?, ?, ?, ?)",
                (vin, make, model, year)
            )
            conn.commit()
            logger.info("Successfully created car record in database")
            car = Car(vin=vin, make=make, model=model, year=year)
            logger.info("Returning car object: %s", car)
            return car

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        logger.info("Looking up car by VIN: %s", vin)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars WHERE vin = ?", (vin,))
            row = cursor.fetchone()
            if not row:
                logger.info("No car found with VIN: %s", vin)
                return None
            
            car = Car(
                vin=row[0],
                make=row[1],
                model=row[2],
                year=row[3]
            )
            logger.info("Found car: %s", car)
            return car
