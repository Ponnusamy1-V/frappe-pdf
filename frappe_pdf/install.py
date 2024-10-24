import asyncio

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from pyppeteer import launch


def get_custom_fields():
    return {
        "Print Settings": [
            {
                "fieldname": "pdf_using_chromium",
                "label": "Generate PDF using Chromium",
                "fieldtype": "Check",
                "insert_after": "pdf_page_width",
            }
        ]
    }


def after_install():
    fields = get_custom_fields()
    create_custom_fields(fields)
    install_pyppeteer_dependencies()


def install_pyppeteer_dependencies():
    async def install():
        browser = await launch(
            headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False
        )
        await browser.close()

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        asyncio.get_event_loop().run_until_complete(install())
    except Exception:
        print("Failed to install pyppeteer dependencies")


def before_uninstall():
    fields = get_custom_fields()
    delete_custom_fields(fields)


def delete_custom_fields(custom_fields):
    """
    :param custom_fields: a dict like `{'doctype': [{fieldname: 'test', ...}]}`
    """

    for doctypes, fields in custom_fields.items():
        if isinstance(fields, dict):
            # only one field
            fields = [fields]

        if isinstance(doctypes, str):
            # only one doctype
            doctypes = (doctypes,)

        for doctype in doctypes:
            frappe.db.delete(
                "Custom Field",
                {
                    "fieldname": ("in", [field["fieldname"] for field in fields]),
                    "dt": doctype,
                },
            )

            frappe.clear_cache(doctype=doctype)
