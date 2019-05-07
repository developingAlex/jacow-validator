from pathlib import Path

from jacowvalidator.docutils.languages import get_language_tags

test_dir = Path(__file__).parent / 'data'


def test_language1():
    from docx import Document
    doc = Document(test_dir / 'floating_table.docx')

    expected = ['en-GB', 'en-US', 'it-IT']
    languages = get_language_tags(doc)
    assert expected == languages, f"languages {languages} do not match expected {expected}"


def test_language2():
    from docx import Document
    doc = Document(test_dir / 'jacow_template_a4.docx')

    expected = ['en-US', 'en-GB', 'ko-KR', 'fr-FR', 'de-CH']
    languages = get_language_tags(doc)
    assert expected == languages, f"languages {languages} do not match expected {expected}"
