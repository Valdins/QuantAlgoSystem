from ..data_processing import DataLoader
from ..config import Config

def main():
    data_loader = DataLoader(Config.ELECTRICITY_PRICE_FILE)
    data = data_loader.load_data()

if __name__ == "__main__":
    main()