from configparser import ConfigParser
from time import sleep
from datetime import datetime

from selenium import webdriver

from util import login, minus_one_month

config = ConfigParser()
config.read("conf.ini")


def create_periodic_iva_declaration():
    driver = webdriver.Chrome(config.get("other", "chromedriver_path"))

    driver.get(config.get("portal_financas", "url_consultar_facturas"))
    driver.fullscreen_window()
    login(driver, config)
    sleep(2)
    tables_recibos = driver.find_elements_by_class_name("tbody-border-primary")
    assert len(tables_recibos) == 1
    table = tables_recibos[0]
    salary = int(table.find_element_by_tag_name("tr").find_elements_by_tag_name("td")[3].text.strip(" €")[:-3].replace('.', ''))

    driver.get(config.get("portal_financas", "url_declaracao_iva"))
    driver.fullscreen_window()
    #login(driver, config)
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

    salary_formatted = str(salary * 100)
    driver.find_element_by_xpath("//input[@name='btOperacoesIsentasSemDeducao']").send_keys(salary_formatted)

    driver.find_element_by_xpath("//button[contains(text(), 'Submeter')]").click()


if __name__ == "__main__":
    create_periodic_iva_declaration()