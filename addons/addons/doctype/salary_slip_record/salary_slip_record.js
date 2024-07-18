// Copyright (c) 2024, abdulbasitali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Slip Record', {
    refresh: function(frm) {
        if (frm.doc.salary_slip_record) {
            frm.add_custom_button(__('Email Salary Slip'), function() {
                let employee_names = [];
                let record_table = frm.doc.salary_slip_record;

                record_table.forEach(element => {
                    if (element.__checked) { // __checked should be checked for truthy value
                        employee_names.push(element.employee);
                    }
                });

                if (employee_names.length > 0) {
                    frappe.call({
                        method: "addons.addons.doctype.salary_slip_record.salary_slip_record.email_salary_slip",
                        args: {
                            name: employee_names,
							start_date : frm.doc.from_date,
							end_date : frm.doc.to_date
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint(r.message);
                            }
                        }
                    });
                } else {
                    frappe.msgprint(__('No salary slips selected.'));
                }
            });
        }
    }
});

