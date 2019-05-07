from pathlib import Path
from docx import Document

from jacowvalidator.test_utils import replace_identifying_text
from jacowvalidator.docutils.references import extract_references

test_dir = Path(__file__).parent / 'data'


def test_tables():
    doc = Document(test_dir / 'jacow_template_a4.docx')
    ref, ref_list = extract_references(doc)

    new_doc = Document(test_dir / 'jacow_template_a4.docx')
    replace_identifying_text(new_doc)
    new_ref, new_ref_list = extract_references(new_doc)

    # compare converted to original
    assert len(ref) == len(new_ref), \
        f"Reference in text count of {len(ref)} does not match original of {len(new_ref)}"
    assert len(ref_list) == len(new_ref_list), \
        f"Reference count of {len(ref_list)} does not match original of {len(new_ref_list)}"
