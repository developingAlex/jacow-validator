from pathlib import Path

from jacowvalidator.utils import extract_references

test_dir = Path(__file__).parent / 'data'


def test_references():
    from docx import Document
    doc = Document(test_dir / 'reference_test.docx')

    # hardcode known issues for the moment
    issues = {
        12: ['order_ok'],
        19: ['used'],
        20: ['order_ok'],
        21: ['order_ok'],
        22: ['order_ok'],
        23: ['order_ok'],
        24: ['order_ok'],
        25: ['order_ok'],
        26: ['order_ok'],
        27: ['order_ok'],
        28: ['order_ok'],
        29: ['order_ok'],
        30: ['order_ok'],
        31: ['order_ok'],
        32: ['order_ok'],
        33: ['order_ok'],
        34: ['order_ok'],
        35: ['order_ok'],
        36: ['order_ok'],
        37: ['order_ok'],
        38: ['order_ok'],
        39: ['order_ok'],
        40: ['order_ok'],
        41: ['order_ok'],
        42: ['order_ok'],
        43: ['order_ok'],
        44: ['order_ok'],
        45: ['order_ok'],
    }
    references_in_text, references_list = extract_references(doc)
    for reference in references_list:
        # TODO optimise this
        if reference['id'] in issues:
            if 'used' in issues[reference['id']]:
                assert reference['used'] is False, f"{reference['id']} used check passes but it should fail"
            else:
                assert reference['used'], f"{reference['id']} used check failed"
        if reference['id'] in issues:
            if 'order_ok' in issues[reference['id']]:
                assert reference['order_ok'] is False, f"{reference['id']} order check passes but it should fail"
            else:
                assert reference['order_ok'], f"{reference['id']} order check failed"
        if reference['id'] in issues:
            if 'style_ok' in issues[reference['id']]:
                assert reference['style_ok'] is False, f"{reference['id']} style check passes but it should fail"
            else:
                assert reference['style_ok'], f"{reference['id']} style check failed"

        else:
            assert reference['used'], f"{reference['id']} used check failed"
            assert reference['order_ok'], f"{reference['id']} order check failed"
            assert reference['style_ok'], f"{reference['id']} style check failed - {reference['style']}"
