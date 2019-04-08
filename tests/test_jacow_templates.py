from pathlib import Path

from jacowvalidator.utils import check_margins, check_margins_A4, get_page_size, check_margins_letter, \
    check_jacow_styles, get_paragraph_style_exceptions, extract_figures, extract_title, get_abstract_and_author


test_dir = Path(__file__).parent / 'data'


# This is an official jacow template so should pass most tests
# It is the below file opened in word and saved as a docx
# https://github.com/t4nec0/JACoW_Templates/raw/master/MSWord/A4/JACoW_W16_A4.dotx
def test_template_a4():
    from docx import Document
    doc = Document(test_dir / 'jacow_template_a4.docx')

    for i, section in enumerate(doc.sections):
        assert get_page_size(section) == 'A4', f"section {i} A4 page size failed"
        assert check_margins_A4(section), f"section {i} A4 margin failed"
        assert check_margins(section), f"section {i} page size / margin combined failed"

    template_test(doc, True)


# This is an official jacow template so should pass most tests
# It is the below file opened in word and saved as a docx
# https://github.com/t4nec0/JACoW_Templates/raw/master/MSWord/Letter/JACoW_W16_Letter.dotx
def test_template_letter():
    from docx import Document
    doc = Document(test_dir / 'jacow_template_letter.docx')

    for i, section in enumerate(doc.sections):
        assert get_page_size(section) == 'Letter', f"section {i} Letter page size failed"
        assert check_margins_letter(section), f"section {i} Letter margin failed"
        assert check_margins(section), f"section {i} page size / margin combined failed"

    template_test(doc, False)


# Common functionality for template tests
# abstract_valid is whether the style for the abstract is correct in the template
def template_test(doc, abstract_valid=False):
    assert check_jacow_styles(doc), "Check Jacow styles failed"

    assert get_paragraph_style_exceptions(doc) == []

    title = extract_title(doc)
    assert title['style_ok'], f"title style check failed - {title['style']}"
    assert title['case_ok'], f"title case check failed - {title['text']}"

    abstract, author = get_abstract_and_author(doc)
    if abstract_valid:
        assert abstract['style_ok'], f"abstract style check failed - {abstract['style']}"
    else:
        assert abstract['style_ok'] is False, f"abstract style check passes but it should fail - {abstract['style']}"
    assert author['style_ok'], f"author case check failed - {author['style']}"

    figures = extract_figures(doc)
    for i, figure in figures.items():
        assert figure['found'], f"figure {figure['name']} not found"
        assert figure['used'], f"figure {figure['name']} not used"
        # the template is not using correct styles so the test should assert false
        assert figure['style_ok'] is False, f"figure {figure['style']} style check passes but it should fail"
