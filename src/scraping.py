# scraping.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import logging

logging.basicConfig(level=logging.INFO)

class WebDriverManager:
    """ Gestiona el ciclo de vida del driver de Selenium. """
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = self.init_driver()

    def init_driver(self):
        """ Inicializa el navegador Firefox con opciones opcionales para headless. """
        options = Options()
        if self.headless:
            options.add_argument('-headless')
        webdriver_service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=webdriver_service, options=options)

    def restart_driver(self):
        """Restart the WebDriver to reset its state, using current headless setting."""
        self.close_driver()
        self.driver = self.init_driver()

    def close_driver(self):
        self.driver.quit()

class Scraper(WebDriverManager):
    WAIT_TIMEOUT = 5
    def __init__(self, headless=True):
        super().__init__(headless)
        self.wait = WebDriverWait(self.driver, self.WAIT_TIMEOUT)
        self.visited_links = set()
        self.companies_data = []
        
    def restart_driver(self):
        """ Simplifica el reinicio usando el método super() """
        super().restart_driver()

    def extract_links(self):
        try:
            links = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".listado-item a[title^='ver detalles de']")))
            return {link.get_attribute("href") for link in links}
        except TimeoutException as e:
            logging.error("Timeout al extraer links: {}".format(e))
        except Exception as e:
            logging.error("Error desconocido al extraer links: {}".format(e))
        return set()

    def extract_company_info(self):
        data = {}
        elements = {
            'Nombre': (By.TAG_NAME, "h1", 'text'),
            'Descripción': (By.CSS_SELECTOR, "p.claim", 'text'),
            'Servicios': (By.CSS_SELECTOR, "div.servicio-domicilio", 'text'),
            'Teléfonos': (By.CSS_SELECTOR, "span.telephone", 'text', True),
            'Dirección': (By.CSS_SELECTOR, "span.address", 'text'),
            'Sitio web': (By.CSS_SELECTOR, "a.sitio-web", 'href'),
            'Horario': (By.CSS_SELECTOR, "time[itemprop='openingHours']", 'text', True)
        }
        for key, value in elements.items():
            try:
                if len(value) == 4:  # When it's a list
                    data[key] = ', '.join([e.text for e in self.driver.find_elements(*value[:2])])
                else:
                    element = self.driver.find_element(*value[:2])
                    data[key] = element.get_attribute(value[2]) if value[2] != 'text' else element.text
            except Exception as e:
                data[key] = None
        return data

    def guardar_info_empresa(self, info, busqueda, localidad):
        clean_info = {}
        for key, value in info.items():
            if isinstance(value, list):
                clean_value = ', '.join(value).replace('\n', ' ').strip()
            else:
                clean_value = value.replace('\n', ' ').strip() if value else ''
            clean_info[key] = clean_value

        record = {
            'Nombre': clean_info.get('Nombre', ''),
            'Descripción': clean_info.get('Descripción', ''),
            'Servicios': clean_info.get('Servicios', ''),
            'Teléfonos': clean_info.get('Teléfonos', ''),
            'Dirección': clean_info.get('Dirección', ''),
            'Sitio web': clean_info.get('Sitio web', ''),
            'Horario': clean_info.get('Horario', ''),
            'Búsqueda': busqueda,
            'Localidad': localidad,
        }
        self.companies_data.append(record)

    def wait_for_element(self, by_type, identifier, timeout=None):
        timeout = timeout or self.WAIT_TIMEOUT
        try:
            return self.wait.until(EC.visibility_of_element_located((by_type, identifier)))
        except TimeoutException:
            return None

    def search(self, busqueda, localidad):
        
        self.driver.get("https://www.paginasamarillas.es/")
        try:
            cookie_accept_btn = self.wait_for_element(By.ID, "onetrust-accept-btn-handler", 5)
            if cookie_accept_btn:
                cookie_accept_btn.click()
            self.wait_for_element(By.ID, "whatInput").send_keys(busqueda)
            self.wait_for_element(By.ID, "where").send_keys(localidad)
            self.wait_for_element(By.ID, "submitBtn").click()

            while True:
                links = self.extract_links()
                for link in links:
                    if link not in self.visited_links:
                        self.visited_links.add(link)
                        self.driver.get(link)
                        info = self.extract_company_info()
                        self.guardar_info_empresa(info, busqueda, localidad)
                next_page = self.get_next_page()
                if not next_page:
                    break
                self.driver.get(next_page)
        except Exception as e:
            logging.error(f"Error during search: {e}")
        finally:
            self.restart_driver()

    def get_next_page(self):
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, 'ul.pagination li a[rel="next"]')
            return next_button.get_attribute('href')
        except Exception:
            return None
        
    def close_driver(self):
        return super().close_driver()