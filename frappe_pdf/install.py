from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    field = {
        "Print Settings": [
            {
                "fieldname": "pdf_using_google_chrome",
                "label": "Generate PDF using Google Chrome",
                "fieldtype": "Check",
                "insert_after": "pdf_page_size"
            }
        ]
    }
    create_custom_fields(field)
