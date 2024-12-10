// Copyright (c) 2024, Josin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project wise Profit and Loss"] = {
	"filters": [
		{
			"fieldname":"company",
			"label":__("Company"),
			"fieldtype":"Link",
			"options":"Company",
			"default": frappe.defaults.get_user_default('Company')
		},
		{
			"fieldname":"account",
			"label":__("Account"),
			"fieldtype":"Link",
			"options":"Account"
		},
		{
			"fieldname":"project",
			"label":__("Project"),
			"fieldtype":"Link",
			"options":"Project"
		},
		{
			"fieldname":"cost_center",
			"label":__("Cost Center"),
			"fieldtype":"Link",
			"options":"Cost Center"
		},
		{
			"fieldname": "is_active",
			"label": __("Is Active"),
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"default": "Yes",
			"width": "40px"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOpen\nCompleted\nCancelled",
			"default": "Open",
			"width": "40px"
		},
		{
			"fieldname":"from_date",
			"label":__("From date"),
			"fieldtype":"Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label":__("To date"),
			"fieldtype":"Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
	]
};
