# core.py
from scraping import Scraper
from data_manager import DataManager
import logging

logging.basicConfig(level=logging.INFO)


class JobFinderScraper:
    def __init__(self, headless):
        self.scraper = Scraper(headless)
        self.data_manager = DataManager()

    def search(self, busqueda, localidad):
        self.data_manager.output_file = f'results/{busqueda}_{localidad}.csv'
        self.scraper.search(busqueda, localidad)
        self.scraper.close_driver()
        for info in self.scraper.companies_data:
            self.data_manager.write_to_csv(info)
            
            
    def close_driver(self):
        return self.scraper.close_driver()