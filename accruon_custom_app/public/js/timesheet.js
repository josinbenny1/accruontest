frappe.ui.form.on('Timesheet', {
    refresh(frm) {
        console.log("Code working for ts")
    },
    validate: function (frm) {
        const standard_hours = 8;
        let total_ot = 0;
        let total_holiday_ot = 0;
        let completed_requests = 0;

        if (!frm.doc.time_logs || frm.doc.time_logs.length === 0) {
            frappe.msgprint(__('No time logs found.'));
            return;
        }


        frm.doc.time_logs.map(function (row) {
            frappe.call({
                method: "accruon_custom_app.api.is_holiday",
                args: {
                    date: row.from_time
                },
                callback: function (response) {
                    const is_holiday = response.message;
                    if (row.hours > standard_hours) {
                        const overtime = row.hours - standard_hours;

                        
                        if (is_holiday) {
                            total_holiday_ot += row.hours;
                        } else {
                            total_ot += overtime;
                        }
                    }

                    
                    completed_requests++;

                    if (completed_requests === frm.doc.time_logs.length) {
                        frm.set_value("custom_total_not", total_ot);
                        frm.set_value("custom_total_hot", total_holiday_ot);
                    }
                }
            });
        });
    }
});
