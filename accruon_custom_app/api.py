import frappe
import frappe.defaults
from frappe.utils import flt
import frappe.utils
from frappe.utils.data import getdate
from frappe import _
import time


@frappe.whitelist()
def is_holiday(date):
    date = frappe.utils.getdate(date)
    company = frappe.defaults.get_defaults("Company")
    holiday_list = frappe.get_doc("Company",company.company)
    holidays = frappe.get_doc("Holiday List", holiday_list.default_holiday_list)
    holiday_dates = [frappe.utils.getdate(h.holiday_date) for h in holidays.holidays]
    return date in holiday_dates





def salaryslip_overtime(doc, method):
    total_hot = 0
    total_not = 0
    for row in doc.timesheets:
        ts = frappe.get_doc("Timesheet",row.time_sheet)
        total_not += ts.custom_total_not if ts.custom_total_not else 0
        total_hot += ts.custom_total_hot if ts.custom_total_hot else 0
    doc.custom_normal_hours = (doc.total_working_hours or 0) - total_hot - total_not

    doc.custom_total_not = total_not
    doc.custom_total_hot = total_hot
    doc.custom_not_hour_rate = (doc.hour_rate or 0) * 1.25
    doc.custom_hot_hour_rate = (doc.hour_rate or 0) * 1.5

    total_not_amount = (total_not * doc.custom_not_hour_rate)
    total_hot_amount = (total_hot * doc.custom_hot_hour_rate)

    hot_row = next((e for e in doc.earnings if e.salary_component == "Holiday OT"), None)
    if hot_row:
        hot_row.amount = total_hot_amount
    else:
        doc.append("earnings", {
            "salary_component": "Holiday OT",
            "amount": total_hot_amount
        })
    not_row = next((e for e in doc.earnings if e.salary_component == "Normal OT"), None)
    if not_row:
        not_row.amount = total_not_amount
    else:
        doc.append("earnings", {
            "salary_component": "Normal OT",
            "amount": total_not_amount
        })
    basic_row = next((e for e in doc.earnings if e.salary_component == "Basic"), None)
    if basic_row:
        basic_row.amount = (doc.custom_normal_hours or 0) * (doc.hour_rate or 0)
    else:
        doc.append("earnings", {
            "salary_component": "Basic",
            "amount": (doc.total_working_hours or 0) * (doc.hour_rate or 0)
        })

    gross_amt = total_not_amount + total_hot_amount + ((doc.custom_normal_hours or 0) * (doc.hour_rate or 0))
    doc.gross_pay = gross_amt

        # doc._is_adjusted = True





def timesheet_overtime(doc, method):
    hrs = frappe.get_doc("HR Settings")
    standard_hours = hrs.standard_working_hours
    total_ot = 0
    total_holiday_ot = 0

    if not doc.time_logs or len(doc.time_logs) == 0:
        frappe.throw(_("No time logs found."))

    for row in doc.time_logs:
        holiday = is_holiday(getdate(row.from_time))
        if holiday:
            total_holiday_ot += row.hours
        else:
            if row.hours > standard_hours:
                overtime = row.hours - standard_hours
                total_ot += overtime

    doc.custom_total_not = flt(total_ot)
    doc.custom_total_hot = flt(total_holiday_ot)

    

def month_find(month):
    months =  {'January':1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
    return months[month]


def make_attendance(doc,event):
    if doc.custom_mark_attendance == 1:
        for t in doc.time_logs:
            newdoc = frappe.get_doc({
                "doctype":"Attendance",
                "employee":doc.employee,
                "attendance_date":t.from_time,
                "status":"Present"
            }).insert()
            newdoc.submit()
    


def update_project_employee(doc,events):
    old_doc = doc.get_doc_before_save()
    for e in doc.custom_employees:
        employee = frappe.get_doc("Employee",e.employee)
        if not employee.custom_project:
            employee.custom_project = doc.name
            employee.save()
    if old_doc and old_doc.custom_employees:
        for oe in old_doc.custom_employees:
            if oe.employee not in doc.custom_employees:
                emp = frappe.get_doc("Employee",oe.employee)
                if emp.custom_project:
                    emp.custom_project = None
                    emp.save()
    
        