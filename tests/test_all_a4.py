from pathlib import Path

from jacowvalidator.utils import check_margins, check_margins_A4, get_page_size, check_jacow_styles, \
    get_paragraph_style_exceptions


test_dir = Path(__file__).parent / 'data'

def test_all_a4_pass():
    from docx import Document

    '''
    correct_all_a4.docx is an official jacow template so should pass all tests
    It is the below file opened in word and saved as a docx
    https://github.com/t4nec0/JACoW_Templates/raw/master/MSWord/A4/JACoW_W16_A4.dotx
    '''
    document = Document(test_dir / 'correct_all_a4.docx')

    assert check_jacow_styles(document), "Check Jacow styles failed"

    for i, section in enumerate(document.sections):
        assert get_page_size(section) == 'A4', f"section {i} A4 page size failed"
        assert check_margins_A4(section), f"section {i} A4 margin failed"
        assert check_margins(section), f"section {i} page size / margin combined failed"

    assert get_paragraph_style_exceptions(document) == []
