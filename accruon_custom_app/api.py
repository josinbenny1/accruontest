import frappe
from frappe.utils import flt
from frappe.utils.data import getdate
from frappe import _


@frappe.whitelist()
def is_holiday(date):
    date = frappe.utils.getdate(date)

    holidays = frappe.get_doc("Holiday List", "india")
    holiday_dates = [frappe.utils.getdate(h.holiday_date) for h in holidays.holidays]
    return date in holiday_dates





def salaryslip_overtime(doc, method):
    # if not hasattr(doc, "_is_adjusted") or not doc._is_adjusted:
    print("Hi****************************************************************************************************")
    total_hot = 0
    total_not = 0
    for row in doc.timesheets:
        total_not += row.get("custom_total_normal_overtime", 0)
        total_hot += row.get("custom_total_holiday_overtime", 0)
    doc.custom_normal_hours = (doc.total_working_hours or 0) - total_hot - total_not

    doc.custom_total_not = total_not
    doc.custom_total_hot = total_hot
    doc.custom_not_hour_rate = (doc.hour_rate or 0) * 1.25
    doc.custom_hot_hour_rate = (doc.hour_rate or 0) * 1.5

    total_amount = (total_not * doc.custom_not_hour_rate) + (total_hot * doc.custom_hot_hour_rate)

    ot_row = next((e for e in doc.earnings if e.salary_component == "OT"), None)
    if ot_row:
        ot_row.amount = total_amount
    else:
        doc.append("earnings", {
            "salary_component": "OT",
            "amount": total_amount
        })

    basic_row = next((e for e in doc.earnings if e.salary_component == "Basic"), None)
    if basic_row:
        basic_row.amount = (doc.custom_normal_hours or 0) * (doc.hour_rate or 0)
    else:
        doc.append("earnings", {
            "salary_component": "Basic",
            "amount": (doc.total_working_hours or 0) * (doc.hour_rate or 0)
        })

        # doc._is_adjusted = True





def timesheet_overtime(doc, method):
    standard_hours = 8
    total_ot = 0
    total_holiday_ot = 0

    if not doc.time_logs or len(doc.time_logs) == 0:
        frappe.throw(_("No time logs found."))

    for row in doc.time_logs:
        holiday = is_holiday(row.from_time)
        
        if row.hours > standard_hours:
            overtime = row.hours - standard_hours

            if holiday:
                total_holiday_ot += row.hours
            else:
                total_ot += overtime

    doc.custom_total_not = flt(total_ot)
    doc.custom_total_hot = flt(total_holiday_ot)

