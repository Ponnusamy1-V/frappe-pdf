import io
import re

import frappe
from frappe.utils import get_url
from frappe.utils.pdf import prepare_options
from frappe_pdf.utils.print_to_pdf import print_to_pdf
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
    html = scrub_urls(html)
    html, options = prepare_options(html, options)

    size = get_page_size(options.get("page-size"))
    if size:
        options["width"] = size.get("width")
        options["height"] = size.get("height")

    content = print_to_pdf(html, options)

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
    returns `width` and `height` for given page size
    """

    paper_sizes = {
        "A0": {"width": "33.1in", "height": "46.8in"},
        "A1": {"width": "23.4in", "height": "33.1in"},
        "A2": {"width": "16.5in", "height": "23.4in"},
        "A3": {"width": "11.7in", "height": "16.5in"},
        "A4": {"width": "8.3in", "height": "11.7in"},
        "A5": {"width": "5.8in", "height": "8.3in"},
        "A6": {"width": "4.1in", "height": "5.8in"},
        "A7": {"width": "2.9in", "height": "4.1in"},
        "A8": {"width": "2.0in", "height": "2.9in"},
        "A9": {"width": "1.5in", "height": "2.0in"},
        "B0": {"width": "39.4in", "height": "55.7in"},
        "B1": {"width": "27.8in", "height": "39.4in"},
        "B2": {"width": "19.7in", "height": "27.8in"},
        "B3": {"width": "13.9in", "height": "19.7in"},
        "B4": {"width": "9.8in", "height": "13.9in"},
        "B5": {"width": "6.9in", "height": "9.8in"},
        "B6": {"width": "4.9in", "height": "6.9in"},
        "B7": {"width": "3.5in", "height": "4.9in"},
        "B8": {"width": "2.4in", "height": "3.5in"},
        "B9": {"width": "1.7in", "height": "2.4in"},
        "B10": {"width": "1.2in", "height": "1.7in"},
        "C5E": {"width": "6.4in", "height": "9.0in"},
        "Comm10E": {"width": "4.1in", "height": "9.5in"},
        "DLE": {"width": "4.3in", "height": "8.7in"},
        "Executive": {"width": "7.25in", "height": "10.5in"},
        "Folio": {"width": "8.5in", "height": "13.0in"},
        "Ledger": {"width": "17.0in", "height": "11.0in"},
        "Legal": {"width": "8.5in", "height": "14.0in"},
        "Letter": {"width": "8.5in", "height": "11.0in"},
        "Tabloid": {"width": "11.0in", "height": "17.0in"},
    }

    return paper_sizes.get(page_size)
