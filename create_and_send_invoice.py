import logging
import os
import smtplib
import sys
from configparser import ConfigParser
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

from selenium import webdriver

config = ConfigParser()
config.read("conf.ini")

download_dir = config.get("other", "download_dir")

chrome_options = webdriver.ChromeOptions()
preferences = {"download.default_directory": download_dir,
               "directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)


def minus_one_month(date):
    if date.month == 1:
        return date.replace(month=12, year=date.year-1)
    else:
        return date.replace(month=date.month-1)


def login(driver):
    logging.info("Logging in.")
    username_field = driver.find_element_by_id("username")
    password_field = driver.find_element_by_id("password")

    username_field.send_keys(config.get("portal_financas", "nif"))
    password_field.send_keys(config.get("portal_financas", "password"))

    driver.find_element_by_name("sbmtLogin").click()


def create_fatura_verde():
    driver = webdriver.Chrome()

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
    last_month_date = minus_one_month(invoice_date)

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

    driver.find_element_by_xpath("//button[text() = 'Emitir']").click()

    sleep(2)

    logging.info("Invoice created.")
    driver.close()


def send_last_invoice_by_email():
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(config.get("portal_financas", "url_consultar_facturas"))
    login(driver)

    sleep(2)

    first_row = driver.find_element_by_xpath('//*[@id="main-content"]/div/div/consultar-app/div[3]/div/div[1]/consultar-tabela/div/div/table/tbody/tr[1]')

    assert "Fatura" in first_row.find_element_by_xpath("td[1]").text

    first_row.find_element_by_xpath("td[last()]//button[2]").click()
    first_row.find_element_by_xpath("//a[text() = 'Imprimir Económico']").click()

    logging.info("Download invoice pdf...")
    sleep(3)

    invoice_emission_date_str = first_row.find_element_by_xpath("td[3]").get_attribute('textContent')
    invoice_emission_date = datetime.strptime(invoice_emission_date_str, "%Y-%m-%d")
    last_months_date = minus_one_month(invoice_emission_date)

    filename = f"txodds_invoice_{last_months_date.year}_{last_months_date.strftime('%B').lower()}.pdf"
    os.rename(f'{download_dir}documento.pdf', f'{download_dir}{filename}')

    logging.info("Sending email...")

    sender_name = config.get("email", "sender_name")
    sender_address = config.get("email", "sender_address")
    sender_password = config.get("email", "sender_password")
    recipient_name = config.get("email", "recipient_name")
    recipient_adress = config.get("email", "recipient_address")
    recipients = [sender_address, recipient_adress]

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = f'{last_months_date.strftime("%B")} Invoice - {sender_name}'
    outer['To'] = ', '.join(recipients)
    outer['From'] = sender_address
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    text = (f"Hello, {recipient_name},\n\n"
            f"Here goes the invoice for the month of {last_months_date.strftime('%B')}. :)\n\n"
            f"Best regards,\n"
            f"{sender_name}")
    outer.attach(MIMEText(text, 'plain'))

    attachments = [f'{download_dir}{filename}']

    # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(sender_address, sender_password)
            s.sendmail(sender_address, recipients, composed)
            s.close()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise


if __name__ == "__main__":
    create_fatura_verde()
    send_last_invoice_by_email()
