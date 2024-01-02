import os
import re
import subprocess
import tempfile
import frappe
from frappe.utils import get_url

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
		r'(href|src)([\s]*=[\s]*[\'"]?)((?:{0})[^\'">]+)([\'"]?)'.format(re.escape(url.replace("https://", "http://")))
	)  # href='https://...
	
	URL_HTTP_NOTATION_PATTERN = re.compile(
		r'(:[\s]?url)(\([\'"]?)((?:{0})[^\'">]+)([\'"]?\))'.format(re.escape(url.replace("https://", "http://")))
	)  # background-image: url('/assets/...')	


	def _expand_relative_urls(match):
		to_expand = list(match.groups())

		if not to_expand[2].startswith(("mailto", "data:", "tel:")):
			if not to_expand[2].startswith(url):
				if not to_expand[2].startswith("/"):
					to_expand[2] = "/" + to_expand[2]
				to_expand.insert(2, url)
		
		# add session id
		if frappe.session and frappe.session.sid and hasattr(frappe.local, "request") and len(to_expand) > 2:
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

def get_pdf(html, *a, **b):
	pdf_file_path = f'/tmp/{frappe.generate_hash()}.pdf'
	html = scrub_urls(html)
	with tempfile.NamedTemporaryFile(mode="w+", suffix=f"{frappe.generate_hash()}.html", delete=True) as html_file:
		html_file.write(html)
		html_file.seek(0)
		chrome_command = [
			"google-chrome",
			"--headless",
			"--disable-gpu",
			"--no-pdf-header-footer",
			"--run-all-compositor-stages-before-draw",
			f"--print-to-pdf={pdf_file_path}",
			html_file.name

		]
		subprocess.run(chrome_command, shell=False)
		content = None
		with open(pdf_file_path, 'rb') as f:
			content = f.read()
		os.remove(pdf_file_path)
	
	return content
