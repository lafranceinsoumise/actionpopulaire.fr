import io
import os
import subprocess

from django.core.files import File
from django.template import engines


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


def render_svg_template(template_file, context):
    with template_file.open() as file:
        django_engine = engines["django"]
        template = django_engine.from_string(file.read().decode())
        return template.render(context)


class TicketGenerationException(Exception):
    pass


RSVG_CONVERT_AVAILABLE_FORMATS = ("pdf", "png", "ps", "svg", "xml")
RSVG_CONVERT_AVAILABLE_FORMAT_CHOICES = ((f, f) for f in RSVG_CONVERT_AVAILABLE_FORMATS)


def rsvg_convert(
    svg, to_format=RSVG_CONVERT_AVAILABLE_FORMATS[0], filename="rsvg-convert"
):
    to_format = to_format.lower()
    if to_format not in RSVG_CONVERT_AVAILABLE_FORMATS:
        raise TicketGenerationException(
            f"Unsupported {to_format} format. Should be one of: {RSVG_CONVERT_AVAILABLE_FORMATS}"
        )

    rsvg = subprocess.Popen(
        [
            "rsvg-convert",
            f"--format={to_format}",
            "--keep-aspect-ratio",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        output, error = rsvg.communicate(input=svg.encode("utf8"), timeout=30)
    except subprocess.TimeoutExpired:
        rsvg.kill()
        rsvg.communicate()
        raise TicketGenerationException("Timeout")

    if rsvg.returncode:
        raise TicketGenerationException("Return code: %d" % rsvg.returncode)

    return File(io.BytesIO(output), name=filename)
