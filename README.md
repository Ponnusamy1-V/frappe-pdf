# Frappe PDF

`frappe_pdf` is an application built on the Frappe framework, designed specifically for rendering PDF files from HTML utilizing Google Chrome's headless mode. It addresses limitations present in wkhtmltopdf, providing better support for modern CSS features and overcoming various rendering constraints.

**Note**: Specify page size and margins in html to get a expected format.

**example**:
```sh
page {
	size: A4;
	margin: 5mm;
}
```

## Features

- **Modern CSS Support:** Utilizes Google Chrome's headless mode to overcome limitations present in wkhtmltopdf, supporting the latest CSS features for more accurate rendering of HTML to PDF.
- **Improved Rendering:** Addresses various constraints and rendering issues encountered with wkhtmltopdf, resulting in better fidelity and consistency in PDF output.

## Why Google Chrome Headless?

Google Chrome's headless mode is preferred due to its robust support for modern web standards, allowing for more accurate and reliable rendering of HTML to PDF compared to wkhtmltopdf. This choice ensures compatibility with the latest CSS features and addresses limitations encountered with wkhtmltopdf.

## Limitations of wkhtmltopdf

- **CSS Support:** wkhtmltopdf may lack support for some of the latest CSS properties and styling, leading to discrepancies in rendering HTML to PDF.
- **Rendering Constraints:** It might struggle with complex layouts, dynamic content, or certain HTML structures, resulting in unexpected rendering issues.

## Installation

### Manual Installation

1. [Install bench](https://frappeframework.com/docs/user/en/installation).
2. Once site is created, get the `frappe-pdf` app

	```sh
	bench get-app https://github.com/Ponnusamy1-V/frappe-pdf.git
	```
3. After that, you can install the `frappe_pdf` app on the site
	```sh
	bench --site sitename install-app frappe_pdf
    ```
4. After installing app on your site, enable the option `Generate PDF using Google Chrome` in `Print Settings`.
5. Google Chrome should be installed on the server. (currently working on replacing the manual installation of google-chrome) 

## Supported Frappe Versions
- version-13
- version-14
- version-15

#### License

mit
