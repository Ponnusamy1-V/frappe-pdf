import subprocess
import tempfile
import frappe
from frappe.utils import scrub_urls
import os

def get_pdf(html, *a, **b):
	pdf_file_path = f'/tmp/{frappe.generate_hash()}.pdf'
	html = scrub_urls(html)
	with tempfile.NamedTemporaryFile(mode="w+", suffix=f"{frappe.generate_hash()}.html", delete=True) as html_file:
		html_file.write(html)
		html_file.seek(0)
		chrome_command = f"""google-chrome --headless --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw  --print-to-pdf='{pdf_file_path}'  {html_file.name} """
		subprocess.run(chrome_command, shell=True)
		content = None
		with open(pdf_file_path, 'rb') as f:
			content = f.read()
		os.remove(pdf_file_path)
	
	return content
