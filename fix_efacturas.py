from configparser import ConfigParser
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from util import login

config = ConfigParser()
config.read("conf.ini")

download_dir = config.get("other", "download_dir")

chrome_options = webdriver.ChromeOptions()
preferences = {"download.default_directory": download_dir,
               "directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)

# Setup
driver = webdriver.Chrome()
driver.get(config.get("portal_financas", "url_emitir_facturas"))
login(driver, config)

ids = []
base_url = "https://faturas.portaldasfinancas.gov.pt/detalheDocumentoAdquirente.action?idDocumento="


for id in ids:
    driver.get(base_url + id)
    sleep(0.5)
    driver.find_element_by_id("alterarDocumentoBtn").click()
    sleep(0.5)
    try:
        driver.find_element_by_id("ambitoActividadeProf").find_element_by_xpath("option[@value=1]").click()
    except NoSuchElementException:
        continue
    sleep(0.5)
    driver.find_element_by_id("guardarDocumentoBtn").click()
    if driver.find_element_by_class_name("alert-error").text != '':
        # Insert breakpoint here
        driver.find_element_by_id("guardarDocumentoBtn").click()

