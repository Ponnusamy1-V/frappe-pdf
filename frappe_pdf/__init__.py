__version__ = "0.0.1"

import frappe
from frappe.utils.pdf import get_pdf
from frappe_pdf.utils.pdf import get_pdf as get_pdf_gc

def pdf(*args, **kwargs):
    if (frappe.db.get_single_value("Print Settings", "pdf_using_google_chrome")):
        return get_pdf_gc(*args, **kwargs)
    else:
        return get_pdf(*args, **kwargs)

frappe.utils.pdf.get_pdf = pdf
