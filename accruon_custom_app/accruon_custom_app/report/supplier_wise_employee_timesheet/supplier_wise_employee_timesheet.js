// Copyright (c) 2024, Josin Benny and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier wise Employee Timesheet"] = {
	"filters": [
		{
			"fieldname":"supplier",
			'fieldtype':"Link",
			"label":"Supplier",
			"options":"Supplier"
		},
		{
			"fieldname":"date",
			"fieldtype":"Date",
			"label":"Date",
			"default":"Today"	
		}

	]
};
