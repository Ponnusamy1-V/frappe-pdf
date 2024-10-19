import io
import os
import re
import shutil
import subprocess
import tempfile

import frappe
from frappe.utils import get_url
from frappe.utils.pdf import prepare_options
from pypdf import PdfReader, PdfWriter

URLS_NOT_HTTP_TAG_PATTERN = re.compile(
    r'(href|src){1}([\s]*=[\s]*[\'"]?)((?!http)[^\'">]+)([\'"]?)'
)  # href=/assets/...
URL_NOT_HTTP_NOTATION_PATTERN = re.compile(
    r'(:[\s]?url)(\([\'"]?)((?!http)[^\'">]+)([\'"]?\))'
)  # background-image: url('/assets/...')


def scrub_urls(html: str) -> str:
    return expand_relative_urls(html)


def expand_relative_urls(html: str) -> str:
    # expand relative urls
    url = get_url()
    if url.endswith("/"):
        url = url[:-1]

    URLS_HTTP_TAG_PATTERN = re.compile(
        r'(href|src)([\s]*=[\s]*[\'"]?)((?:{0})[^\'">]+)([\'"]?)'.format(
            re.escape(url.replace("https://", "http://"))
        )
    )  # href='https://...

    URL_HTTP_NOTATION_PATTERN = re.compile(
        r'(:[\s]?url)(\([\'"]?)((?:{0})[^\'">]+)([\'"]?\))'.format(
            re.escape(url.replace("https://", "http://"))
        )
    )  # background-image: url('/assets/...')

    def _expand_relative_urls(match):
        to_expand = list(match.groups())

        if not to_expand[2].startswith(("mailto", "data:", "tel:")):
            if not to_expand[2].startswith(url):
                if not to_expand[2].startswith("/"):
                    to_expand[2] = "/" + to_expand[2]
                to_expand.insert(2, url)

        # add session id
        if (
            frappe.session
            and frappe.session.sid
            and hasattr(frappe.local, "request")
            and len(to_expand) > 2
        ):
            if "?" in to_expand[-2]:
                to_expand[-2] += f"&sid={frappe.session.sid}"
            else:
                to_expand[-2] += f"?sid={frappe.session.sid}"

        return "".join(to_expand)

    html = URLS_HTTP_TAG_PATTERN.sub(_expand_relative_urls, html)
    html = URLS_NOT_HTTP_TAG_PATTERN.sub(_expand_relative_urls, html)
    html = URL_NOT_HTTP_NOTATION_PATTERN.sub(_expand_relative_urls, html)
    html = URL_HTTP_NOTATION_PATTERN.sub(_expand_relative_urls, html)

    return html


def get_pdf(html, options=None, output: PdfWriter | None = None):
    pdf_file_path = f"/tmp/{frappe.generate_hash()}.pdf"
    html = scrub_urls(html)
    html, options = prepare_options(html, options)

    additional_style = ""
    if options:
        if options.get("page-height") or options.get("page-width"):
            additional_style += f"""<style>
            @page {{
                size: {options.get("page-width")}mm {options.get("page-height")}mm;
            }}
            </style>"""

        elif options.get("page-size"):
            additional_style += f"""<style>
            @page {{
                size: {
                    f'''{size.get("width")}in {size.get("height")}in'''
                    if (size:=get_page_size(options.get("page-size"))) 
                    else options.get("page-size")
                };
            }}
            </style>"""

        if (
            options.get("margin-top")
            or options.get("margin-bottom")
            or options.get("margin-left")
            or options.get("margin-right")
        ):
            additional_style += f"""<style>
            @page {{
                {" ".join([f"{key}: {options.get(key)};" for key in ("margin-top", "margin-bottom", "margin-left", "margin-right") if options.get(key)])}
            }}
            </style>"""

    html = additional_style + html

    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=f"{frappe.generate_hash()}.html", delete=True
    ) as html_file:
        html_file.write(html)
        html_file.seek(0)
        chrome_command = [
            "google-chrome"
            if shutil.which("google-chrome")
            else "google-chrome-stable",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={pdf_file_path}",
            html_file.name,
        ]
        subprocess.run(chrome_command, shell=False)
        content = None
        with open(pdf_file_path, "rb") as f:
            content = f.read()
        os.remove(pdf_file_path)

    reader = PdfReader(io.BytesIO(content))

    if output:
        output.append_pages_from_reader(reader)
        return output

    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    if "password" in options:
        password = options["password"]
        writer.encrypt(password)

    filedata = get_file_data_from_writer(writer)

    return filedata


def get_file_data_from_writer(writer_obj):
    # https://docs.python.org/3/library/io.html
    stream = io.BytesIO()
    writer_obj.write(stream)

    # Change the stream position to start of the stream
    stream.seek(0)

    # Read up to size bytes from the object and return them
    return stream.read()


def get_page_size(page_size):
    """
    paper sizes are in inches
    """

    paper_sizes = {
        "A0": {"width": 33.1, "height": 46.8},
        "A1": {"width": 23.4, "height": 33.1},
        "A2": {"width": 16.5, "height": 23.4},
        "A3": {"width": 11.7, "height": 16.5},
        "A4": {"width": 8.3, "height": 11.7},
        "A5": {"width": 5.8, "height": 8.3},
        "A6": {"width": 4.1, "height": 5.8},
        "A7": {"width": 2.9, "height": 4.1},
        "A8": {"width": 2.0, "height": 2.9},
        "A9": {"width": 1.5, "height": 2.0},
        "B0": {"width": 39.4, "height": 55.7},
        "B1": {"width": 27.8, "height": 39.4},
        "B2": {"width": 19.7, "height": 27.8},
        "B3": {"width": 13.9, "height": 19.7},
        "B4": {"width": 9.8, "height": 13.9},
        "B5": {"width": 6.9, "height": 9.8},
        "B6": {"width": 4.9, "height": 6.9},
        "B7": {"width": 3.5, "height": 4.9},
        "B8": {"width": 2.4, "height": 3.5},
        "B9": {"width": 1.7, "height": 2.4},
        "B10": {"width": 1.2, "height": 1.7},
        "C5E": {"width": 6.4, "height": 9.0},
        "Comm10E": {"width": 4.1, "height": 9.5},
        "DLE": {"width": 4.3, "height": 8.7},
        "Executive": {"width": 7.25, "height": 10.5},
        "Folio": {"width": 8.5, "height": 13.0},
        "Ledger": {"width": 17.0, "height": 11.0},
        "Legal": {"width": 8.5, "height": 14.0},
        "Letter": {"width": 8.5, "height": 11.0},
        "Tabloid": {"width": 11.0, "height": 17.0},
    }

    return paper_sizes.get(page_size)
