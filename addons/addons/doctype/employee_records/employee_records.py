# Copyright (c) 2024, abdulbasitali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

class EmployeeRecords(Document):
    def validate(self):
        self.employee_record = []
        self.populate_sales_invoice_table()

    def populate_sales_invoice_table(self):
        if self.from_date and self.to_date:
            employee_without_email = []
            base_query = """
                SELECT
                    employee
                FROM
                    `tabEmployee`
                WHERE
                    date_of_joining BETWEEN '{0}' AND '{1}' AND status = 'Active'
            """.format(self.from_date, self.to_date)
            # Execute the query
            salary_slip_record = frappe.db.sql(base_query, as_dict=1)

            if salary_slip_record:
                for salary_slip in salary_slip_record:
                    employee_email = frappe.db.get_value("Employee", salary_slip.get("employee"), "prefered_email")
                    if employee_email:
                        self.append("employee_record", {
                            "employee": salary_slip.get("employee"),
                            "email": employee_email
                        })
                    else:
                        employee_without_email.append(salary_slip.get("employee"))
                if employee_without_email:
                    employee_links = ", ".join([
                        '<a href="/app/Employee/{0}">{0}</a>'.format(employee)
                        for employee in employee_without_email
                    ])
                    frappe.msgprint("These Employees Don't have Email: {0}".format(employee_links))

@frappe.whitelist()
def email_salary_slip(name, start_date, end_date):
    import json
    
    if isinstance(name, str):
        name = json.loads(name)

    for employee in name:
        receiver = frappe.db.get_value("Employee", employee, "prefered_email", cache=True)
        # payroll_settings = frappe.get_single("Payroll Settings")

        subject = "Salary Slip - from {0} to {1}".format(start_date, end_date)
        message = _("Please see attachment")
        # if payroll_settings.email_template:
        #     email_template = frappe.get_doc("Email Template", payroll_settings.email_template)
        #     context = {"start_date": start_date, "end_date": end_date, "employee": employee}
        #     subject = frappe.render_template(email_template.subject, context)
        #     message = frappe.render_template(email_template.response, context)

        # password = None
        # if payroll_settings.encrypt_salary_slips_in_emails:
        #     password = generate_password_for_pdf(payroll_settings.password_policy, employee)
        #     if not payroll_settings.email_template:
        #         message += "<br>" + _(
        #             "Note: Your salary slip is password protected, the password to unlock the PDF is of the format {0}."
        #         ).format(payroll_settings.password_policy)

        if receiver:
            email_args = {
                "sender": "Admin",
                "recipients": [receiver],
                "message": message,
                "subject": subject,
                "attachments": [
                    frappe.attach_print("Employee", employee, file_name=employee, password=None)
                ],
                "reference_doctype": "Employee",
                "reference_name": employee,
            }
            frappe.sendmail(**email_args)
        else:
            frappe.msgprint(_("{0}: Employee email not found, hence email not sent").format(employee))

def generate_password_for_pdf(policy_template, employee):
	employee = frappe.get_cached_doc("Employee", employee)
	return policy_template.format(**employee.as_dict())