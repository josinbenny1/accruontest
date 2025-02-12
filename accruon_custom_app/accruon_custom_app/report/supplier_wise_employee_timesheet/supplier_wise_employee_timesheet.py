# Copyright (c) 2024, Josin Benny and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_last_day,format_date,date_diff,get_first_day,add_days,get_datetime,today
from accruon_custom_app.api import month_find
from datetime import datetime


def execute(filters=None):
    if filters.get("project"):
        project_name = frappe.get_value("Project", filters.get("project"), "project_name")

        filters["project_name"] = project_name
    
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    
    
    return columns, data


def get_columns(filters):
    columns = [
        {
            'fieldname': 'employee',
            'label': _('Employee'),
            'fieldtype': 'Link',
            'options': 'Employee',
            'width': 150
        },
        {
            'fieldname': 'employee_name',
            'label': _('Employee Name'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'employee_type',
            'label': _('Emp Type'),
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'fieldname': 'supplier',
            'label': _('Supplier'),
            'fieldtype': 'Link',
            'options': 'Supplier',
            'width': 100
        },
        {
            'fieldname': 'project',
            'label': _('Project'),
            'fieldtype': 'Link',
            'options': 'Project',
            'width': 100
        }
    ]
    if not filters.get('summary'):
        if filters.get("from_date") and filters.get("to_date"):
            
            first_day = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
            last_day = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
            no_of_days = date_diff(last_day, first_day) + 1
            for i in range(1, no_of_days + 1):
                date_label = add_days(first_day,i-1)
                row = {
                    'fieldname': str(i),
                    'label': f"{date_label}",
                    'fieldtype': 'Float',
                    'width':110
                }
                columns.append(row)
    ot = [
        {
            'fieldname': 'empty',
            'label': _(''),
            'fieldtype': 'data',
        },
        {
            'fieldname': 'not',
            'label': _('N OT'),
            'fieldtype': 'Float',
        },
        {
            'fieldname': 'hot',
            'label': _('H OT'),
            'fieldtype': 'Float',
        },
        {
            'fieldname':'normal_hours',
            'label':_('Normal Hours'),
            'fieldtype':'float'
        },
        {
            'fieldname':'total_hours',
            'label':_('Total Hours'),
            'fieldtype':'float'
        }
    ]
    columns.extend(ot)

    return columns




def get_data(filters):
    timesheets = frappe.get_all(
        "Timesheet",
        filters={"docstatus": 1},
        fields=["name", "employee", "creation", "custom_total_not", "custom_total_hot", "total_hours"]
    )

    filter_conditions = get_conditions(filters)
    data = {}
    
    employees = {e.name: e for e in frappe.get_all("Employee", filters=filter_conditions, fields=["name", "employee_name", "custom_employee_type", "custom_supplier", "custom_project"])}

    suppliers_timesheets = [t for t in timesheets if t.employee in employees] if filters else timesheets
    
    if filters.get("from_date") and filters.get("to_date"):
        first_day = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
        last_day = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
        no_of_days = date_diff(last_day, first_day) + 1
        previous_day = add_days(first_day, -1)

        time_logs = frappe.get_all(
            "Timesheet Detail",
            filters={"parent": ["in", [t.name for t in suppliers_timesheets]], "from_time": ["between", [previous_day, last_day]]},
            fields=["parent", "hours", "from_time"]
        )

        time_log_map = {}
        for log in time_logs:
            time_log_map.setdefault(log["parent"], []).append(log)

        for timesheet in suppliers_timesheets:
            emp = employees.get(timesheet.employee)
            supplier = emp.custom_supplier if emp and emp.custom_employee_type == "Supplier Provided" else ""
            supplier_det = frappe.get_doc("Supplier", supplier) if supplier else None
            project = frappe.get_value("Project", emp.custom_project, "project_name") if emp and emp.custom_project else None

            if timesheet.employee not in data:
                data[timesheet.employee] = {
                    'employee': timesheet.employee,
                    'supplier': supplier,
                    'employee_name': emp.employee_name if emp else "",
                    'employee_type': emp.custom_employee_type if emp else "",
                    'project': project,
                    'not': 0,
                    'hot': 0,
                    'normal_hours': 0,
                    'total_hours': 0,
                }
                for day in range(1, no_of_days + 1):
                    data[timesheet.employee][str(day)] = 0

            data[timesheet.employee]['not'] += timesheet.custom_total_not
            data[timesheet.employee]['hot'] += timesheet.custom_total_hot
            data[timesheet.employee]['normal_hours'] += (timesheet.total_hours - timesheet.custom_total_not - timesheet.custom_total_hot)
            data[timesheet.employee]['total_hours'] += timesheet.total_hours

            for log in time_log_map.get(timesheet.name, []):
                log_date = log["from_time"].date()
                day_number = (log_date - first_day).days + 1
                if 1 <= day_number <= no_of_days:
                    data[timesheet.employee][str(day_number)] += log.hours

                    if not filters.get("raw_data") and supplier_det and supplier_det.custom_is_ot_applicable == 0:
                        if data[timesheet.employee][str(day_number)] >= supplier_det.custom_standard_working_hours:
                            data[timesheet.employee][str(day_number)] = supplier_det.custom_standard_working_hours

    else:
        frappe.msgprint("Please set From Date and To Date")

    return list(data.values())

def get_conditions(filters):
    filter = {}
    if filters.get("supplier"):
        filter["custom_supplier"] = filters.get("supplier")
        filter["custom_employee_type"] = "Supplier Provided"
    if filters.get("project"):
        filter["custom_project"] = filters.get("project")
    return filter
