from pathlib import Path

from jacowvalidator.margins import check_margins_A4


test_dir = Path(__file__).parent / 'data'


def test_a4_margins_pass():
    from docx import Document

    document = Document(test_dir / 'correct_a4_margins.docx')

    for section in document.sections:
        assert check_margins_A4(section)
