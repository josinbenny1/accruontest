# Copyright (c) 2024, Josin Benny and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_last_day,format_date,date_diff,get_first_day,add_days,get_datetime


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data




# def get_columns(filters):
# 	columns =  [
# 		{
# 		'fieldname':'employee',
# 		'label':_('Employee'),
# 		'fieldtype':'Link',
# 		'options':'Employee',
# 		'width':300
# 		}
# 	]
# 	if filters.get("date"):
# 		date = format_date(filters.get("date"))
# 		first_day = get_first_day(date)
# 		last_day = get_last_day(date)
# 		no_of_days = date_diff(last_day,first_day) + 1
# 		for i in range(1,no_of_days+1):
# 			row = {
# 					'fieldname':str(i),
# 					'label':_(str(i)),
# 					'fieldtype':'float',
# 				}
# 			columns.append(row)
#     ot = [
#             {
#                 'fieldname':'not',
#                 'label':_('N OT'),
#                 'fieldtype':'float',
#             },
#             {
#                 'fieldname':'hot',
#                 'label':_('H OT'),
#                 'fieldtype':'float',
#             }
#     ]
#     columns.extend(ot)

# 	return columns

def get_columns(filters):
    columns = [
        {
            'fieldname': 'employee',
            'label': _('Employee'),
            'fieldtype': 'Link',
            'options': 'Employee',
            'width': 300
        }
    ]
    if not filters.get('summary'):
        print(filters.get('summary'))
        if filters.get("date"):
            date = format_date(filters.get("date"))
            first_day = get_first_day(date)
            last_day = get_last_day(date)
            no_of_days = date_diff(last_day, first_day) + 1
            for i in range(1, no_of_days + 1):
                row = {
                    'fieldname': str(i),
                    'label': _(str(i)),
                    'fieldtype': 'Float',
                    'width':50
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
        fields=["name", "employee", "creation","custom_total_not","custom_total_hot","total_hours"]
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
            previous_day = add_days(first_day, -1)
            print(previous_day,last_day)
            time_logs = frappe.get_all(
                "Timesheet Detail",
                filters = {
                            "parent": timesheet.name,
                            "from_time":["between",[previous_day,last_day]]
                           },
                fields = ["hours", "from_time"]
            )

            row['not'] = 0
            row['hot'] = 0
            row['normal_hours'] = 0
            row['total_hours'] = 0
            if time_logs:
                row['not'] += timesheet.custom_total_not
                row['hot'] += timesheet.custom_total_hot
                row['normal_hours'] += timesheet.total_hours - timesheet.custom_total_not - timesheet.custom_total_hot
                row['total_hours'] += timesheet.total_hours
            else:
                pass
            for log in time_logs:
                print(log)
                log_date = log["from_time"].date() 
                day_number = (log_date - first_day).days + 1
                if 1 <= day_number <= no_of_days:
                    row[str(day_number)] += log.hours

            data.append(row)

    return data
