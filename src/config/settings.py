import os

class Config:

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Data files paths
    DATA_FOLDER = os.path.join(BASE_DIR, "data")
    ELECTRICITY_PRICE_FILE = os.path.join(DATA_FOLDER, "electricity_prices.csv")