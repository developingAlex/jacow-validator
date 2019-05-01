from pathlib import Path

from jacowvalidator.references import extract_references


test_dir = Path(__file__).parent / 'data'


def test_references():
    from docx import Document
    doc = Document(test_dir / 'reference_test.docx')

    # hard code known issues for the moment
    type_of_checks = ['used', 'order_ok', 'style_ok']
    issues = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: [],
        9: [],
        10: [],
        11: [],
        12: ['order_ok'],
        13: [],
        14: [],
        15: [],
        16: [],
        17: [],
        18: [],
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
    assert len(references_list) == 45

    for item in references_list:
        # TODO optimise this
        for check in type_of_checks:
            if check in issues[item['id']]:
                assert item[check] is False, f"{item['id']} {check} check passes but it should fail"
            else:
                assert item[check], f"{item['id']} {check} check failed"
