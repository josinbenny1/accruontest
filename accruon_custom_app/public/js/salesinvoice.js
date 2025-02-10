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



async function salesInvoiceItem(frm) {
    const items = {};
    frm.set_value('items', []);
    frappe.dom.freeze("Please wait..");

    if (frm.doc.timesheets && frm.doc.timesheets.length > 0) {
        const promises = frm.doc.timesheets.map(async (row) => {
            try {
                const response = await frappe.db.get_value("Activity Type", { name: row.activity_type }, "custom_item");
                const item = response.message?.custom_item;
                console.log("1 works");

                if (item) {
                    const rates = await frappe.call({
                        method: "accruon_custom_app.api.get_rates",
                        args: {
                            "data": row,
                            "project": frm.doc.project
                        }
                    });

                    let data = rates.message[0];
                    if (items[item]) {
                        items[item].qty += row.billing_hours;
                        items[item].rate = (items[item].rate + (row.billing_amount / row.billing_hours)) / 2;
                        items[item].not += data.not;
                        items[item].hot += data.hot;
                        items[item].normal_hours += data.normal_hours;
                        items[item].ot_rate = data.ot_rate;
                        items[item].normal_rate = data.billing_price;
                    } else {
                        items[item] = {
                            item_code: item,
                            rate: row.billing_amount / row.billing_hours,
                            qty: row.billing_hours,
                            not: data.not,
                            hot: data.hot,
                            normal_hours: data.normal_hours,
                            ot_rate: data.ot_rate,
                            normal_rate: data.billing_price
                        };
                    }
                }
            } catch (error) {
                console.error(`Error fetching custom_item for Activity Type: ${row.activity_type}`, error);
            }
        });

        await Promise.all(promises);
        addItemstoInvoice(frm, items);
        console.log("2 works");

    } else {
        frappe.dom.unfreeze();
    }
}



function addItemstoInvoice(frm, items) {
    
    if (frm.doc.items && frm.doc.items.length > 1){

        } else {
        for (const item in items) {
            const child = frm.add_child("items");
            child.item_code = items[item].item_code;
            child.rate = (((items[item].not)*(items[item].ot_rate * 1.25))+((items[item].hot)*(items[item].ot_rate * 1.5))+((items[item].normal_hours)*(items[item].normal_rate)));
            child.qty = 1;
            child.uom = "Hour";
            child.item_name = items[item].item_code;
            child.custom_total_not = items[item].not;
            child.custom_total_hot = items[item].hot;
            child.custom_normal_hours = items[item].normal_hours;
            child.custom_not_rate = (items[item].ot_rate * 1.25);
            child.custom_hot_rate = (items[item].ot_rate * 1.5);
            child.custom_normal_rate = (items[item].normal_rate);
            
        }
    frm.refresh_field("items");
    frappe.dom.unfreeze()
    }
}
