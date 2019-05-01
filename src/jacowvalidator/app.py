import os
from datetime import datetime
from subprocess import run

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from flask import Flask, redirect, render_template, request, url_for, send_file

from flask_uploads import UploadSet, configure_uploads, UploadNotAllowed

from .utils import (
    check_jacow_styles,
    check_margins,
    get_abstract_and_author,
    extract_figures,
    extract_references,
    extract_title,
    get_margins,
    get_page_size,
    get_language_tags,
    get_language_tags_location,
)
from .test_utils import (
    replace_identifying_text,
)
from .tables import (
    check_table_titles,
)

documents = UploadSet("document", ("docx"))

try:
    p = run(['git', 'log', '-1', '--format=%h,%at'], capture_output=True, text=True, check=True)
    commit_sha, commit_date = p.stdout.split(',')
    commit_date = datetime.fromtimestamp(int(commit_date))
except Exception:
    commit_sha, commit_date = None, None

app = Flask(__name__)
app.config.update(
    dict(UPLOADS_DEFAULT_DEST=os.environ.get("UPLOADS_DEFAULT_DEST", "/var/tmp"))
)

configure_uploads(app, (documents,))


@app.context_processor
def inject_commit_details():
    return dict(commit_sha=commit_sha, commit_date=commit_date)


@app.template_filter('tick_cross')
def tick_cross(s):
    return "✓" if s else "✗"


@app.route("/")
def hello():
    return redirect(url_for('upload'))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST" and documents.name in request.files:
        try:
            filename = documents.save(request.files[documents.name])
        except UploadNotAllowed:
            return render_template("upload.html", error=f"Wrong file extension. Please upload .docx files only")
        fullpath = documents.path(filename)

        try:
            doc = Document(fullpath)

            jacow_styles_ok = check_jacow_styles(doc)

            # get page size and margin details
            sections = []
            for i, section in enumerate(doc.sections):
                sections.append(
                    (
                        get_page_size(section),
                        check_margins(section),
                        get_margins(section),
                    )
                )

            # get title and title syle details
            title = extract_title(doc)
            abstract, authors = get_abstract_and_author(doc)
            figures = extract_figures(doc)
            references_in_text, references_list = extract_references(doc)
            table_titles = check_table_titles(doc)
            language_summary = get_language_tags(doc)
            languages = get_language_tags_location(doc)

            return render_template("upload.html", processed=True, **locals())
        except PackageNotFoundError:
            return render_template("upload.html", error=f"Failed to open document {filename}. Is it a valid Word document?")
        except OSError:
            return render_template("upload.html", error=f"It seems the file {filename} is corrupted")
        except Exception:
            if app.debug:
                raise
            else:
                app.logger.exception("Failed to process document")
                return render_template("upload.html", error=f"Failed to process document: {filename}")
        finally:
            os.remove(fullpath)

    return render_template("upload.html")


@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST" and documents.name in request.files:
        filename = documents.save(request.files[documents.name])
        full_path = documents.path(filename)
        try:
            doc = Document(full_path)
            new_doc_path = documents.path('test_'+filename)
            replace_identifying_text(doc, new_doc_path)
            # send_file should handle the open read and close
            return send_file(
                new_doc_path,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                attachment_filename=filename
            )

        finally:
            os.remove(full_path)
            # PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: '/var/tmp\\document\\test_THPMK148_2.docx'
            # only happens on windows I think.
            os.remove(new_doc_path)

    return render_template("convert.html")