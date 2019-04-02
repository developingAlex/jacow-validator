from pathlib import Path

from jacowvalidator.utils import check_margins_A4


testdir = Path(__file__).parent / 'data'


def test_a4_margins_pass():
    from docx import Document

    document = Document(testdir / 'correct_a4_margins.docx')

    for section in document.sections:
        assert check_margins_A4(section)
