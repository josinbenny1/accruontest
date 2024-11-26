frappe.ui.form.on('Salary Slip', {
    refresh(frm) {
        console.log("Code working for SS")
    },
    // validate: function(frm) {
    //     setTimeout(() => {
    //         let total_hot = 0;
    //         let total_not = 0;
    
    //         frm.doc.timesheets.forEach(function(row) {
    //             total_not += row.custom_total_normal_overtime || 0;
    //             total_hot += row.custom_total_holiday_overtime || 0;
    //         });
    
    //         frm.set_value("total_working_hours", frm.doc.total_working_hours - total_hot - total_not);
    
    //         frm.set_value('custom_total_not', total_not);
    //         frm.set_value('custom_total_hot', total_hot);
    //         frm.set_value('custom_not_hour_rate', (frm.doc.hour_rate * 1.25));
    //         frm.set_value('custom_hot_hour_rate', (frm.doc.hour_rate * 1.5));
    
    //         let total_amount = (total_not * frm.doc.custom_not_hour_rate) + (total_hot * frm.doc.custom_hot_hour_rate);
    
    //         let existing_ot_row = frm.doc.earnings.find(e => e.salary_component === "OT");
    //         if (existing_ot_row) {
    //             existing_ot_row.amount = total_amount; 
    //         } else {
    //             let new_row = frm.add_child('earnings');
    //             new_row.salary_component = "OT";
    //             new_row.amount = total_amount;
    //         }
    
    //         frm.refresh_field('earnings');
    //     },500);
    // }
    validate: function(frm) {
        setTimeout(() => {
            // Use a client-side flag to prevent recalculation
            if (!frm.is_adjusted) {
                let total_hot = 0;
                let total_not = 0;

                // Calculate overtime totals
                frm.doc.timesheets.forEach(function(row) {
                    total_not += row.custom_total_normal_overtime || 0;
                    total_hot += row.custom_total_holiday_overtime || 0;
                });

                // Adjust total working hours
                frm.set_value("total_working_hours", frm.doc.total_working_hours - total_hot - total_not);

                // Update custom fields for overtime
                frm.set_value('custom_total_not', total_not);
                frm.set_value('custom_total_hot', total_hot);
                frm.set_value('custom_not_hour_rate', (frm.doc.hour_rate * 1.25));
                frm.set_value('custom_hot_hour_rate', (frm.doc.hour_rate * 1.5));

                // Calculate total amount for OT
                let total_amount = (total_not * frm.doc.custom_not_hour_rate) + (total_hot * frm.doc.custom_hot_hour_rate);

                // Update or add "OT" to earnings
                let existing_ot_row = frm.doc.earnings.find(e => e.salary_component === "OT");
                if (existing_ot_row) {
                    existing_ot_row.amount = total_amount;
                } else {
                    let new_row = frm.add_child('earnings');
                    new_row.salary_component = "OT";
                    new_row.amount = total_amount;
                }
                let existing_basic = frm.doc.earnings.find(e => e.salary_component === "Basic");
                if (existing_basic) {
                    existing_basic.amount = (frm.doc.total_working_hours * frm.doc.hour_rate);
                } else {
                    let new_row = frm.add_child('earnings');
                    new_row.salary_component = "Basic";
                    new_row.amount = (frm.doc.total_working_hours * frm.doc.hour_rate);
                }

                // Mark as adjusted to avoid re-calculation
                frm.is_adjusted = true;
            }

            // Refresh fields to reflect changes
            frm.refresh_field('earnings');
        },500);
    }
});
