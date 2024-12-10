# Copyright (c) 2024, Josin and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    cs_data = get_cs_data(filters)

    if not cs_data:
        msgprint(_("No records found"))
        return columns, []

    data = []
    grand_total = {"account_number": "<strong>Grand Total</strong>"}

    for d in cs_data:
        account=frappe.get_doc("Account",d["account"])
        row = {
        "accounts": d["account"],
        "account_number": account.account_number
    }

        for c in columns[1:]:
            project_name = c["fieldname"]

            project_entry = next((p for p in d["projects"] if p["project"] == project_name), None)


            if project_entry:
                profit = project_entry["profit"]
                row[project_name] = profit

                grand_total[project_name] = grand_total.get(project_name, 0) + profit
        data.append(row)

    grand_total_row = frappe._dict(grand_total)
    data.append(grand_total_row)

    return columns, data




def get_columns(filters):
    conditions = get_conditions(filters)
    if conditions.get("company"):
        if conditions.get("project"):
            projects = frappe.get_all(
                "Project", 
                filters={"name": conditions.get("project"), 
                         "company": conditions.get("company"),
                         "is_active":conditions.get("is_active"),
                         "status":conditions.get("status")})
        else:
            projects = frappe.get_all(
                "Project", 
                filters={"company": conditions.get("company"),
                         "is_active":conditions.get("is_active"),
                         "status":conditions.get("status")})
    else:
        projects = frappe.get_all(
                "Project",
                filters={"is_active":conditions.get("is_active"),
                         "status":conditions.get("status")})

    columns = [
        {
            "fieldname": "account_number",
            "label": "Account Number",
            "fieldtype": "Data",
            "width": "150"
        },
        {
            "fieldname": "accounts",
            "label": "Accounts",
            "fieldtype": "Link",
            "width": "400",
            "options": "Account"
        }
    ]

    for d in projects:
        proj=frappe.get_doc("Project",d.name)
        columns.append({
            "fieldname": d.name,
            "label": proj.project_name,
            "fieldtype": "data",
            "width": "150"
        })
    if conditions.get("cost_center"):
        cost_centr = frappe.get_all(
                "Cost Center", 
                filters={"name": conditions.get("cost_center"), 
                         "company": conditions.get("company")})
    else:
        cost_centr = frappe.get_all(
                "Cost Center",
                filters={"company": conditions.get("company")})
        
    for c in cost_centr:
        cc = frappe.get_doc("Cost Center", c.name)
        columns.append({
            "fieldname": c.name,
            "label": cc.cost_center_name,
            "fieldtype": "data",
            "width": "150"
        })
    return columns


def get_conditions(filters):
    conditions = {}
    for key, value in filters.items():
        if value:
            conditions[key] = value

    return conditions



def get_cs_data(filters):
    conditions = get_conditions(filters)
    if "company" in conditions and conditions["company"]:
        if "account" in conditions and conditions["account"]:
            accounts = frappe.get_all(
                "Account", 
                filters=dict(name=conditions["account"],
                company =conditions["company"],
                root_type = "Income"),
                order_by="lft")
            expense_accounts = frappe.get_all(
                "Account", 
                filters=dict(name=conditions["account"],
                company =conditions["company"],
                root_type = "Expense"),
                order_by="lft")
        else:
            accounts = frappe.get_all(
                "Account", 
                filters=dict(company =conditions["company"],
                root_type = "Income"),
                order_by="lft")
            expense_accounts = frappe.get_all(
                "Account", 
                filters=dict(company =conditions["company"],
                root_type = "Expense"),
                order_by="lft")
    else:
        accounts = frappe.get_all(
            "Account", 
            filters=dict(root_type = "Income"),
            order_by="lft")
        expense_accounts = frappe.get_all(
            "Account", 
            filters=dict(root_type = "Expense"),
            order_by="lft")
        

    accounts += expense_accounts

    csd = []

    for acc in accounts:
        account_entry = {"account": acc.name, "projects": []}
        if conditions.get("from_date"):
            gle_entries = frappe.get_all(
                "GL Entry",
                fields=["account", "project", "debit", "credit","posting_date","cost_center"],
                filters=dict(account=acc.name,
                            posting_date=[">=",conditions["from_date"]],
                            
                )
            )

        else:
            gle_entries = frappe.get_all(
                "GL Entry",
                fields=["account", "project", "debit", "credit","posting_date","cost_center"],
                filters=dict(account=acc.name)
            )
            
        if conditions.get("to_date"):
            for gle in gle_entries:
                to_date_obj = datetime.strptime(conditions["to_date"], '%Y-%m-%d').date()
                if gle["posting_date"] <= to_date_obj:
                    
                    if gle["project"] or gle["cost_center"]:
                        prof = gle["credit"] - gle["debit"]
                        pe=False
                        for p in account_entry["projects"]:
                            if p["project"] == gle["project"]:
                                p["profit"]+=prof
                                pe=True
                                break
                        if not pe and  gle["project"]:
                            account_entry["projects"].append({
                            "project": gle["project"],
                            "profit": prof
                        })
                        for p in account_entry["projects"]:
                            if p["project"] == gle["cost_center"] and not gle["project"]:
                                p["profit"]+=prof
                                pe=True
                                break
                        
                        if not pe and gle["cost_center"] and not gle["project"]:
                            account_entry["projects"].append({
                            "project": gle["cost_center"],
                            "profit": prof
                        })
                    

        else:
            for gle in gle_entries:
                if gle["project"]  or gle["cost_center"]:
                    prof = gle["credit"] - gle["debit"]
                    pe=False
                    for p in account_entry["projects"]:
                        if p["project"] == gle["project"]:
                            p["profit"]+=prof
                            pe=True
                            break
                    if not pe and  gle["project"]:
                        account_entry["projects"].append({
                        "project": gle["project"],
                        "profit": prof
                    })
                    for p in account_entry["projects"]:
                        if p["project"] == gle["cost_center"] and not gle["project"]:
                            p["profit"]+=prof
                            pe=True
                            break
                    
                    if not pe and gle["cost_center"] and not gle["project"]:
                        account_entry["projects"].append({
                        "project": gle["cost_center"],
                        "profit": prof
                    })
                    
                
        csd.append(account_entry)
        
    return csd