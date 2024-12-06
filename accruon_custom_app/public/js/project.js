frappe.ui.form.on('Project', {
    refresh(frm) {
        frm.add_custom_button(__("Create Sales Invoice"), function() {
            frappe.model.with_doctype('Sales Invoice', function() {
                var new_doc = frappe.model.get_new_doc('Sales Invoice');
                new_doc.customer = frm.doc.customer; 
                new_doc.project = frm.doc.name;
                frappe.set_route('Form', 'Sales Invoice', new_doc.name);
            });
        });
    },
    onload: function(frm) {
        frm.set_query("employee", "custom_employees", function(doc, cdt, cdn) {
            return {
                filters: {
                    custom_project: "" 
                }
            };
        });
    }
});


frappe.ui.form.on('Project Employee Details', {
	employee: function(frm,cdt,cdn){
        let row = locals[cdt][cdn];
        if (row.employee) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Employee',
                    name: row.employee, 
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'costing_price', r.message.custom_costing_rate);
                        frappe.model.set_value(cdt, cdn, 'billing_price', r.message.custom_billing_rate);
                        frappe.model.set_value(cdt, cdn, 'activity', r.message.custom_activity);
                    }
                }
            });
        }
    }
})