import enum
from typing import Annotated
from livekit.agents import llm
import logging
from db_driver import DatabaseDriver


logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

logger.info("Initializing API module")
DB = DatabaseDriver()
logger.info("Database driver initialized")

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"


class AssistantFnc(llm.FunctionContext):
    def __init__(self) -> None:
        logger.info("Initializing AssistantFnc")
        super().__init__()
        
        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: ""
        }
        logger.info("Car details initialized: %s", self._car_details)

    @llm.ai_callable(description="lookup a card by its vin")
    def lookup_car(
        self,
        vin: Annotated[int, llm.TypeInfo(description="The vin of the car to lookup")]
    ):
        logger.info("Entering lookup_car function with VIN: %s", vin)
        
        result = DB.get_car_by_vin(vin)
        if result is None:
            logger.info("No car found for VIN: %s", vin)
            return "Car not found"
        
        logger.info("Car found, updating car details state")
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        logger.info("Updated car details: %s", self._car_details)

        car_str = ""
        for key, value in self._car_details.items():
            car_str += f"{key}: {value}\n"
        
        logger.info("Returning car details string")
        return f"The car details are: {car_str}"

    @llm.ai_callable(description="get the car details of the current car")
    def get_car_details(
        self
    ):
        logger.info("Entering get_car_details function")
        logger.info("Current car details state: %s", self._car_details)
        
        car_str = ""
        for key, value in self._car_details:
            car_str += f"{key}: {value}\n"
        
        return f"The car details are: {car_str}"

    @llm.ai_callable(description="create a new car")
    def create_car(
        self,
        vin: Annotated[str, llm.TypeInfo(description="The vin of the car to create")],
        make: Annotated[str, llm.TypeInfo(description="the make of the car")],
        model: Annotated[str, llm.TypeInfo(description="the model of the car")],
        year: Annotated[int, llm.TypeInfo(description="the year of the car")]
    ):
        logger.info("Entering create_car function")
        logger.info("Parameters - VIN: %s, Make: %s, Model: %s, Year: %s", vin, make, model, year)
        
        result = DB.create_car(vin, make, model, year)
        if result is None:
            logger.error("Failed to create car in database")
            return "Failed to create car"
        
        logger.info("Car created successfully, updating car details state")
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        logger.info("Updated car details: %s", self._car_details)
        
        return "Car created"
    
    def has_car(self):
        logger.info("Checking if car exists in current state")
        has_car = self._car_details[CarDetails.VIN] != ""
        logger.info("Has car: %s", has_car)
        return has_car
