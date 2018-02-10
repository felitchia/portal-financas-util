from configparser import ConfigParser
from datetime import datetime
from time import sleep

from util import login

from selenium import webdriver


config = ConfigParser()
config.read("conf.ini")


def create_last_months_receipt():
    driver = webdriver.Chrome(config.get("other", "chromedriver_path"))

    driver.get(config.get("portal_financas", "url_emitir_recibos"))

    login(driver, config)

    sleep(3)

    first_row = driver.find_element_by_xpath("//tbody/tr[1]")

    assert "Fatura" in first_row.find_element_by_xpath("td[1]").text, "The first row doesn't contain an invoice"

    invoice_date_str = first_row.find_element_by_xpath("td[2]").get_attribute('textContent')
    invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")

    assert datetime.today().month == invoice_date.month, "It's expected that the invoice in the first row was created in the current month"

    first_row.find_element_by_xpath("td[5]").click()

    radio_button_to_click = driver.find_element_by_xpath("//label/input[@value=1]/..")
    assert radio_button_to_click.text == "Pagamento dos bens ou dos serviços"
    radio_button_to_click.click()

    driver.find_element_by_xpath("//option[@label = 'Sem retenção - Não residente sem estabelecimento']").click()

    driver.find_element_by_xpath("//button[text() = 'Emitir']").click()
    sleep(1)
    driver.find_element_by_xpath("//div[@class = 'modal-dialog']//button[text() = 'Emitir']").click()


if __name__ == "__main__":
    create_last_months_receipt()