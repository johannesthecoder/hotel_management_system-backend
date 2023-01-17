from enum import Enum


class MeasurementUnit(str, Enum):
    # weight related
    KG = "kg"
    GRAM = "gram"
    A_100_GRAM = "a 100 gram"
    A_150_GRAM = "a 150 gram"
    A_200_GRAM = "a 200 gram"
    QUARTER_KG = "quarter kg"
    HALF_KG = "half kg"
    ONE_THIRD_KG = "one third kg"
    FLOUR_PACK = "flour pack"

    # volume related
    LITER = "liter"
    MILLILITER = "milliliter"
    JUICE_GLASS = "juice glass"
    TEA_CUP = "tea cup"
    SODA_BOTEL = "soda botel"
    PLASTIC_SODA_BOTEL = "plastic soda botel"

    # count related
    PIECE = "piece"
    BUNCH = "bunch"
    TRAY = "tray"
    DOZEN = "dozen"
    SAUSAGE_PACK = "sausage pack"


measurement_unit_value = {
    "kg": 1000,
    "gram": 1,
    "a 100 gram": 100,
    "a 150 gram": 150,
    "a 200 gram": 200,
    "quarter kg": 250,
    "half kg": 500,
    "one third kg": 750,
    "flour pack": 2000,
    "liter": 1000,
    "milliliter": 1,
    "juice glass": 350,
    "tea cup": 300,
    "soda_botel": 300,
    "plastic soda botel": 500,
    "piece": 1,
    "bunch": 1,
    "tray": 30,
    "dozen": 12,
    "sausage pack": 22,
}

measurement_unit_nickname = {
    "juice glass": "glass",
    "tea cup": "cup",
    "soda_botel": "botel",
    "plastic soda botel": "plastic",
}
