import subprocess

import os


def html_to_pdf(html_content, dest_path=None):
    if dest_path is None:
        dest_path = "-"

    process = subprocess.run(
        ["wkhtmltopdf", "--encoding", "utf-8", "-", dest_path],
        input=html_content.encode(),
        capture_output=True,
        timeout=10,
        check=True,
    )

    return process


def join_pdf_documents(pdfs, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # https://stackoverflow.com/questions/2507766/merge-convert-multiple-pdf-files-into-one-pdf

    process = subprocess.run(
        [
            "ghostscript",
            "-dBATCH",  # Causes Ghostscript to exit after processing all files
            "-dNOPAUSE",  # Disables the prompt and pause at the end of each page.
            "-q",  # Quiet startup
            "-sDEVICE=pdfwrite",  # Sélectionne la sortie en PDF
            f"-sOutputFile={dest_path}",
            *[str(p) for p in pdfs],
        ]
    )

    return process
