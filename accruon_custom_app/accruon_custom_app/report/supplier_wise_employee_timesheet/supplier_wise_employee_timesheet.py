# Copyright (c) 2024, Josin Benny and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_last_day,format_date,date_diff,get_first_day


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data




def get_columns(filters):
	columns =  [
		{
		'fieldname':'employee',
		'label':_('Employee'),
		'fieldtype':'Link',
		'options':'Employee',
		'width':300
		}
	]
	if filters.get("date"):
		date = format_date(filters.get("date"))
		first_day = get_first_day(date)
		last_day = get_last_day(date)
		no_of_days = date_diff(last_day,first_day) + 1
		for i in range(1,no_of_days+1):
			row = {
					'fieldname':str(i),
					'label':_(str(i)),
					'fieldtype':'int',
				}
			columns.append(row)
	return columns

def get_data(filters):
    timesheets = frappe.get_all(
        "Timesheet",
        filters={"docstatus": 1},
        fields=["name", "employee", "creation"]
    )
    suppliers_timesheets = []
    data = []

    if filters.get("supplier"):
        employees = frappe.get_all(
            "Employee",
            filters={"custom_supplier": filters.get("supplier")},
            fields=["name"]
        )
        employee_names = {e.name for e in employees}

        suppliers_timesheets = [
            t for t in timesheets if t.employee in employee_names
        ]
    else:
        suppliers_timesheets = timesheets

    if filters.get("date"):
        date = format_date(filters.get("date"))
        first_day = get_first_day(date)
        last_day = get_last_day(date)
        no_of_days = date_diff(last_day, first_day) + 1

        for timesheet in suppliers_timesheets:
            row = {
                'employee': timesheet.employee,
            }

            for day in range(1, no_of_days + 1):
                row[str(day)] = 0.0

            time_logs = frappe.get_all(
                "Timesheet Detail",
                filters={"parent": timesheet.name},
                fields=["hours", "from_time"]
            )

            for log in time_logs:
                log_date = log.from_time.date() 
                day_number = (log_date - first_day).days + 1
                if 1 <= day_number <= no_of_days:
                    row[str(day_number)] += log.hours

            data.append(row)

    return data
