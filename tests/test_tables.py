from pathlib import Path

from jacowvalidator.tables import check_table_titles

test_dir = Path(__file__).parent / 'data'

def test_tables():
    from docx import Document
    doc = Document(test_dir / 'jacow_template_a4.docx')

    # hardcode known issues with this doc for the moment
    issues = {
        1: [],
        2: ['style_ok'],
        3: ['used','order_ok'],
    }
    table_titles = check_table_titles(doc)
    for table in table_titles:
        # TODO optimise this
        if 'used' in issues[table['id']]:
            assert table['used'] == 0, f"{table['id']} used check passes but it should fail"
        else:
            assert table['used'] > 0, f"{table['id']} used check failed"

        if 'order_ok' in issues[table['id']]:
            assert table['order_ok'] is False, f"{table['id']} order check passes but it should fail"
        else:
            assert table['order_ok'], f"{table['id']} order check failed"

        if 'style_ok' in issues[table['id']]:
            assert table['style_ok'] is False, f"{table['id']} style check passes but it should fail"
        else:
            assert table['style_ok'], f"{table['id']} style check failed"

