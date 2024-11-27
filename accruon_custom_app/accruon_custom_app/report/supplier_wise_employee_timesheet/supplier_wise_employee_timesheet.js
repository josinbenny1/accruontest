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
			"fieldname": "year",
			"fieldtype": "Select",
			"label": "Year",
			"options": [],
			"default": frappe.datetime.get_today().split("-")[0]  
		},
		
		{
			"fieldname":"date",
			"fieldtype":"Select",
			"label":"Month",
			"options":['January',"February","March","April","May","June","July","August","September","October","November","December"]	
		},
		{
			"fieldname":"summary",
			"fieldtype":"Check",
			"label":"Summary",
			"default":0	
		},


	],
	onload: function (report) {
        let currentYear = new Date().getFullYear();
        let yearOptions = [];
        for (let year = 2000; year <= currentYear; year++) {
            yearOptions.push(year.toString());
        }

        report.page.fields_dict.year.df.options = yearOptions.join("\n");
        report.page.fields_dict.year.refresh();
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
