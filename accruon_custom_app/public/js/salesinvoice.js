frappe.ui.form.on('Sales Invoice', {
	refresh: function (frm) {
        frm.remove_custom_button('Fetch Timesheet');
		if (frm.doc.docstatus === 0 && !frm.doc.is_return) {
			frm.add_custom_button(__("Fetch Timesheets"), function () {
				let d = new frappe.ui.Dialog({
					title: __("Fetch Timesheet"),
					fields: [
						{
							label: __("From"),
							fieldname: "from_time",
							fieldtype: "Date",
							reqd: 1,
						},
						{
							fieldtype: "Column Break",
							fieldname: "col_break_1",
						},
						{
							label: __("To"),
							fieldname: "to_time",
							fieldtype: "Date",
							reqd: 1,
						},
						{
							label: __("Project"),
							fieldname: "project",
							fieldtype: "Link",
							options: "Project",
							default: frm.doc.project,
						},
					],
					primary_action: function () {
						const data = d.get_values();
						frm.events.add_timesheet_data(frm, {
							from_time: data.from_time,
							to_time: data.to_time,
							project: data.project,
						}).then(()=>{
                            frm.set_value("custom_timesheet_from", data.from_time)
                            frm.set_value("custom_timesheet_to", data.to_time)
                        salesInvoiceItem(frm)
                    })
						d.hide();
                        
					},
					primary_action_label: __("Get Timesheets"),
				});
				d.show();
                
			});
		}
        
		if (frm.doc.is_debit_note) {
			frm.set_df_property("return_against", "label", __("Adjustment Against"));
		}
        
	},

})




function salesInvoiceItem(frm) {
    const items = {};
    frm.set_value('items', []);
    frappe.dom.freeze("Please wait..")

    if (frm.doc.timesheets && frm.doc.timesheets.length > 0){
        const promises = frm.doc.timesheets.map((row) => {
            return frappe.db.get_value("Activity Type", { name: row.activity_type }, "custom_item")
                .then((response) => {
                    const item = response.message?.custom_item;

                    if (item) {
                        if (items[item]) {
                            items[item].qty += row.billing_hours;
                            items[item].rate = (items[item].rate + (row.billing_amount / row.billing_hours)) / 2;
                        } else {
                            items[item] = {
                                item_code: item,
                                rate: row.billing_amount / row.billing_hours,
                                qty: row.billing_hours
                            };
                        }
                    }
                })
                .catch((error) => {
                    console.error(`Error fetching custom_item for Activity Type: ${row.activity_type}`, error);
                });
        });
        Promise.all(promises).then(() => {
            console.log(items);
            addItemstoInvoice(frm, items);
        });
    } else {
        console.log("No Data Found")
        frappe.dom.unfreeze()
    }

    
}



function addItemstoInvoice(frm, items) {
    console.log("Adding items to invoice...");
    if (frm.doc.items && frm.doc.items.length > 1){

        } else {
        for (const item in items) {
            const child = frm.add_child("items");
            child.item_code = items[item].item_code;
            child.rate = items[item].rate;
            child.qty = items[item].qty;
            child.uom = "Hour";
            child.item_name = items[item].item_code;
            console.log("Child item added:", child);
            
        }
    frm.refresh_field("items");
    frappe.dom.unfreeze()
    }
}
