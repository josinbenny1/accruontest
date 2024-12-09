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
			"fieldname":"project",
			'fieldtype':"Link",
			"label":"Project",
			"options":"Project"
		},
		{
			"fieldname":"from_date",
			"fieldtype":"Date",
			"label":"FromDate"
		},
		{
			"fieldname":"to_date",
			"fieldtype":"Date",
			"label":"To Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"summary",
			"fieldtype":"Check",
			"label":"Summary",
			"default":0	
		},


	],
	onload: function (report) {
        let today = new Date();
		let previousMonthDate = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
		let formattedPreviousMonthDate = frappe.datetime.obj_to_str(previousMonthDate);

		report.page.fields_dict.from_date.set_input(formattedPreviousMonthDate);
    },
	
	"formatter": function (value, row, column, data, default_formatter) {
        let formatted_value = default_formatter(value, row, column, data);
		if (column.fieldtype === "Float" && value != null) {
            value = parseFloat(value).toFixed(2);
            formatted_value = `<div>${value}</div>`;
        }
		
        if (column.fieldname === "not") {
            formatted_value = `<div style="background-color: lightgreen; padding: 5px;">${value}</div>`;
        } else if (column.fieldname === "hot") {
            formatted_value = `<div style="background-color: orange; padding: 5px;">${value}</div>`;
        } else if (column.fieldname === "normal_hours") {
            formatted_value = `<div style="background-color: blueviolet; color: white; padding: 5px;">${value}</div>`;
        }else if (column.fieldname === "total_hours") {
            formatted_value = `<div style="background-color: red; color: white; padding: 5px;">${value}</div>`;
		}
        return formatted_value;
    }
};
