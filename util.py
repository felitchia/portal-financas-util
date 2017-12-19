def minus_one_month(date):
    if date.month == 1:
        return date.replace(month=12, year=date.year-1)
    else:
        return date.replace(month=date.month-1)


def login(driver, config):
    username_field = driver.find_element_by_id("username")
    password_field = driver.find_element_by_id("password")

    username_field.send_keys(config.get("portal_financas", "nif"))
    password_field.send_keys(config.get("portal_financas", "password"))

    driver.find_element_by_name("sbmtLogin").click()