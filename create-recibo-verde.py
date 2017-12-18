import logging
from configparser import ConfigParser
from datetime import datetime

import requests
from selenium import webdriver

config = ConfigParser()
config.read("conf.ini")

chrome_options = webdriver.ChromeOptions()
preferences = {"download.default_directory": config.get("other", "download_dir"),
               "directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)

driver = webdriver.Chrome(chrome_options=chrome_options)

def login(driver):
    logging.info("Logging in.")
    username_field = driver.find_element_by_id("username")
    password_field = driver.find_element_by_id("password")

    username_field.send_keys(config.get("portal_financas", "nif"))
    password_field.send_keys(config.get("portal_financas", "password"))

    driver.find_element_by_name("sbmtLogin").click()

def create_recibo_verde():
    logging.info("Entering page.")
    driver.get(config.get("portal_financas", "url_emitir_facturas"))

    login(driver)

    logging.info("Filling form.")

    # Date
    today = datetime.today()
    invoice_day = config.get('portal_financas', 'invoice_day')

    invoice_date = datetime(today.year, today.month, int(invoice_day))
    invoice_date_str = invoice_date.strftime("%Y-%m-%d")
    invoice_date_field = driver.find_element_by_xpath("//input[@name='dataPrestacao']")
    invoice_date_field.send_keys(invoice_date_str)

    # Type of invoice
    driver.find_element_by_xpath("//option[@label='Fatura']").click()

    # Info about company
    company_country = config.get('company', "company_country").upper()
    driver.find_element_by_xpath(f"//option[contains(@label, '{company_country}')]").click()

    company_code_field = driver.find_element_by_xpath("//input[@name='nifEstrangeiro']")
    company_code_field.send_keys(config.get("company", "company_code"))

    company_name_field = driver.find_element_by_xpath("//input[@name='nomeAdquirente']")
    company_name_field.send_keys(config.get("company", "company_name"))

    # Final info
    last_month_date = invoice_date.replace(month = 12 if invoice_date.month == 1 else invoice_date.month - 1)

    description = (f'Monthy fee {last_month_date.strftime("%Y-%m-%d")} - {invoice_date.strftime("%Y-%m-%d")}\n' 
                    'Bank account information:\n' 
                   f'IBAN: {config.get("bank_account_info", "iban")}\n'
                   f'SWIFT/BIC: {config.get("bank_account_info", "swift")}')

    description_field = driver.find_element_by_xpath("//textarea[@name='servicoPrestado']")
    description_field.send_keys(description)

    driver.find_element_by_xpath("//option[@label='Regras de localização - art.º 6.º [regras especificas]']").click()

    salary = str(int(config.get("company", "salary")) * 100)
    salary_field = driver.find_element_by_xpath("//input[@name='valorBase']")
    salary_field.send_keys(salary)

    # driver.find_element_by_xpath("//button[text() = 'Emitir']").click()

    logging.info("Invoice created.")

def send_last_invoice_by_email():
    driver.get(config.get("portal_financas", "url_consultar_facturas"))
    login(driver)
    driver.find_element_by_xpath("//a[text() = 'Imprimir Económico']").click()
    driver

if __name__ == "__main__":
    # create_recibo_verde()
    send_last_invoice_by_email()
