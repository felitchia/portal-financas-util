from configparser import ConfigParser
from time import sleep
from datetime import datetime

from selenium import webdriver

from util import login, minus_one_month

config = ConfigParser()
config.read("conf.ini")


def create_periodic_iva_declaration():
    driver = webdriver.Chrome(config.get("other", "chromedriver_path"))

    driver.get(config.get("portal_financas", "url_declaracao_iva"))
    driver.fullscreen_window()
    login(driver, config)
    sleep(2)

    today = datetime.today()
    today_last_month = minus_one_month(today)

    driver.find_element_by_xpath("//select[@name = 'localizacaoSede']/option[@title = 'Continente']").click()
    driver.find_element_by_xpath(f"//select[@name = 'anoDeclaracao']/option[@title = '{today_last_month.year}']").click()
    driver.find_element_by_xpath(f"//select[@name = 'periodoDeclaracao']//option[@title = '{today_last_month.strftime('%m')}']").click()
    driver.find_element_by_xpath("//select[@name = 'prazo']/option[@title = 'Dentro do prazo']").click()

    driver.find_element_by_xpath("//a[text() = ' Apuramento ']").click()

    driver.find_element_by_xpath("//lf-radio[@lf-label = 'Tem operações em que liquidou e/ou autoliquidou imposto?']//input[@value='N']").click()
    driver.find_element_by_xpath("//lf-radio[@lf-label = 'Tem operações em que não liquidou imposto?']//input[@value='S']").click()
    driver.find_element_by_xpath("//lf-radio[@lf-label = 'Tem imposto dedutível e/ou regularizações?']//input[@value='N']").click()
    driver.find_element_by_xpath("//lf-radio[@lf-catalog = 'apuramento-tem-operacoes-adquirente-com-liq-imposto']//input[@value = '02']").click()

    salary = str(int(config.get('company', 'salary')) * 100)
    driver.find_element_by_xpath("//input[@name='btOperacoesIsentasSemDeducao']").send_keys(salary)

    driver.find_element_by_xpath("//button[contains(text(), 'Submeter')]").click()


if __name__ == "__main__":
    create_periodic_iva_declaration()