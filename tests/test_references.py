from pathlib import Path

from jacowvalidator.utils import extract_references

test_dir = Path(__file__).parent / 'data'


# This is an official jacow template so should pass most tests
# It is the below file opened in word and saved as a docx
# https://github.com/t4nec0/JACoW_Templates/raw/master/MSWord/A4/JACoW_W16_A4.dotx
def test_references():
    from docx import Document
    doc = Document(test_dir / 'reference_test.docx')

    references_in_text, references_list = extract_references(doc)
    for reference in references_list:
        assert reference['used'], f"{reference['id']} used check failed"
        assert reference['order_ok'], f"{reference['id']} order check failed"
        assert reference['style_ok'], f"{reference['id']} style check failed - {reference['style']}"
