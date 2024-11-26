import frappe


@frappe.whitelist()
def is_holiday(date):
    date = frappe.utils.getdate(date)

    holidays = frappe.get_doc("Holiday List", "india")
    holiday_dates = [frappe.utils.getdate(h.holiday_date) for h in holidays.holidays]
    return date in holiday_dates
