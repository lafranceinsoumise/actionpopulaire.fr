from pathlib import Path

from django.template import loader
from tempfile import TemporaryDirectory

from agir.lib.documents import html_to_pdf, join_pdf_documents


def generate_cost_certificate(data, dest_path):
    html_content = loader.render_to_string("municipales/cost_certificate.html", data)

    with TemporaryDirectory() as dir:
        pdf_certificate_path = Path(dir) / "certificate.pdf"
        html_to_pdf(html_content, dest_path=pdf_certificate_path)

        join_pdf_documents(
            [pdf_certificate_path, str(Path(__file__).parent / "facture_grenier.pdf")],
            dest_path,
        )
