import os
from docx import Document

from flask import Flask, request, render_template
from flask_uploads import UploadSet, configure_uploads

from utils import check_jacow_styles, get_page_size, check_margins
from utils import RE_REFS, RE_FIG_INTEXT, RE_FIG_TITLES

documents = UploadSet("document", ("docx"))

app = Flask(__name__)
app.config.update(
    dict(UPLOADS_DEFAULT_DEST=os.environ.get("UPLOADS_DEFAULT_DEST", "/var/tmp"))
)

configure_uploads(app, (documents,))


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST" and documents.name in request.files:
        filename = documents.save(request.files[documents.name])
        fullpath = documents.path(filename)
        try:
            doc = Document(fullpath)
            report = []
            references = []
            figures_refs = []
            figures_titles = []

            report.append((check_jacow_styles(doc), "JACoW Styles"))
            report.append((True, f"Found {len(doc.sections)} sections"))

            for i, section in enumerate(doc.sections):
                report.append((True, f"Section {i} page size {get_page_size(section)}"))
                report.append((check_margins(section), f"Section {i} margins"))

            for i, p in enumerate(doc.paragraphs):
                if i == 0:
                    # title
                    report.append(
                        (p.style.name == "JACoW_Paper Title", "Paper Title Style")
                    )
                if i == 1:
                    # author list
                    report.append(
                        (p.style.name == "JACoW_Author List", "Author List Style")
                    )
                if i == 2:
                    # abstract heading
                    report.append(
                        (
                            p.style.name == "JACoW_Abstract_Heading",
                            "Abstract Heading Style",
                        )
                    )

                # find reference markers in text
                for ref in RE_REFS.findall(p.text):
                    references.append(ref)

                # find figures
                for f in RE_FIG_INTEXT.findall(p.text):
                    figures_refs.append(f)
                for f in RE_FIG_TITLES.findall(p.text):
                    figures_titles.append(f)

            return render_template(
                "upload.html",
                report=report,
                processed=filename,
                references=references,
                figures_refs=figures_refs,
                figures_titles=figures_titles,
            )
        finally:
            os.remove(fullpath)

    return render_template("upload.html")
