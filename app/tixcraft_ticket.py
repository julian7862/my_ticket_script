from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

def tixcraft_ticket_agree(driver):
    """點選同意票券購買條款。"""
    try:
        form_checkbox = driver.find_element(By.ID, 'TicketForm_agree')
        if form_checkbox.is_enabled() and not form_checkbox.is_selected():
            form_checkbox.click()
        return True
    except Exception as exc:
        print("Failed to click TicketForm_agree:", exc)
        return False

def tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number):
    """自動填入購票數量。"""
    try:
        select_obj.select_by_visible_text(ticket_number)
        return True
    except Exception as exc:
        print(f"Failed to select {ticket_number} tickets:", exc)
        return False

def tixcraft_ticket_main(driver, config_dict):
    """購票主要流程，包括同意條款和選擇票數。"""
    if config_dict["auto_check_agree"]:
        tixcraft_ticket_agree(driver)

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
        select_obj = Select(form_select) if form_select.is_enabled() else None
    except Exception as exc:
        print("Failed to find or enable the ticket select box:", exc)
        select_obj = None

    is_ticket_number_assigned = False
    if select_obj:
        try:
            if select_obj.first_selected_option.text != "0":
                is_ticket_number_assigned = True
        except Exception as exc:
            print("Error reading selected ticket option:", exc)

    if not is_ticket_number_assigned:
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)

    return is_ticket_number_assigned
