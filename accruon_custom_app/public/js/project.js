frappe.ui.form.on("Project", "onload", function(frm) {
    frm.set_query("employee", "custom_employees", function(doc, cdt, cdn) {
        return {
            filters: {
                custom_project : ""
            }
        };
    });
});
