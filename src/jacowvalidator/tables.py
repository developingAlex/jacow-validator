import re
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl, CT_TblPr
from docx.table import _Cell, _Row, Table
from docx.text.paragraph import Paragraph
from .utils import get_paragraph_alignment


RE_TABLE_LIST = re.compile(r'^Table \d+:')
RE_TABLE_ORDER = re.compile(r'^Table \d+')
RE_TABLE_REF_LIST = re.compile(r'Table \d+')
RE_TABLE_FORMAT = re.compile(r'\.$')
RE_TABLE_TITLE_CAPS = re.compile(r'^(?:[A-Z][^\s]*\s?)+$')
RE_REMOVE_SPECIAL = re.compile(r'[^a-zA-Z ]|(of|and|to)')


def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    elif isinstance(parent, _Row):
        parent_elm = parent._tr
    else:
        raise ValueError("something's not right")

    # TODO make this work for floating tables
    # as do not necessarily appear in the same order in the document as they do visually
    # Floating tables can be fixed in word doc by right clicking in table, choosing table properties,
    # selecting None for text wrapping and clicking on ok.
    # Then moving the table to the correct place.
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            # check whether floating
            # CT_TblPr
            # for c in child.iterchildren():
            #     print(c)
            #     if isinstance(c, CT_TblPr):
            #         for c2 in c.iterchildren():
            #             print(c2)
            yield Table(child, parent)


def check_caption_format(title, format_checks):
    result = True
    message = []
    for check in format_checks:
        text = title.text.strip()
        if check['preformat']:
            text = check['preformat'].sub("", text)
            # remove extra spaces created by preformat
            text = re.sub(' +', ' ', text)

        if check['valid_result'] is True and check['test'].search(text) is None:
            result = False
            message.append(check['message'])
        elif check['valid_result'] is False and check['test'].search(text) is not None:
            result = False
            message.append(check['message'])

    return result, message


def check_table_titles(doc):
    """
    Table captions are actually titles, this means that they are in Title Case, and don’t have a “.”
    At the end, well unless exceeds 2 lines.  The table caption is centred if 1 line (“Table Caption” Style),
    and Justified if 2 or more (“Table Caption Multi Line” Style.  The table caption must appear above the Table.

    All tables must be numbered in the order they appear in the document and not skip a number in the sequence.

    All tables start with “Table n:”.
    All tables must be referred to in the main text and use “Table n”.
    """
    prev = None
    table_details = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            prev = block
        elif isinstance(block, Table):
            # exclude those with only 1 column, since not likely to be real tables.
            if len(block.columns) == 1:
                continue

            # check whether there is data in table
            text_found = False
            for row in block.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip() is not '':
                            text_found = True
                            break

            if text_found:
                table_details.append({'table': block, 'title': prev})

    refs = []
    table_titles = [item['title'].text for item in table_details]
    for paragraph in doc.paragraphs:
        # don't include if it is one of the table titles
        if paragraph.text not in table_titles:
            # Check for table names
            result = RE_TABLE_REF_LIST.findall(paragraph.text)
            if result is not None:
                for f in result:
                    refs.append(f)

    title_details = []
    count = 1

    table_caption_format_checks = [
        {
            'test': RE_TABLE_LIST,
            'valid_result': True,
            'message': 'Does not use "Table N: " format',
            'preformat': False
        },
        {
            'test': RE_TABLE_FORMAT,
            'valid_result': False,
            'message': 'Has a . at the end of the sentence',
            'preformat': False
        },
        {
            'test': RE_TABLE_TITLE_CAPS,
            'valid_result': True,
            'message': 'Not in Title Caps',
            'preformat': RE_REMOVE_SPECIAL
        },
    ]

    for table in table_details:
        title = table['title']
        result, message = check_caption_format(title, table_caption_format_checks)

        order_check = RE_TABLE_ORDER.findall(title.text.strip())
        # TODO Add info if doing some common wrong ways of doing references like 'table 1'
        used_count = refs.count('Table ' + str(count))

        title_details.append({
            'id': count,
            'text': title.text,
            'text_format_ok': result,
            'text_format_message': '\n'.join(message),
            'used': used_count,
            'order_ok': f'Table {count}' in order_check,
            'style': title.style.name,
            'style_ok': title.style.name in ['Caption', 'Table Caption', 'Table Caption Multi Line'],
            'alignment': get_paragraph_alignment(title),
            'table': f"rows: {len(table['table'].rows)}, columns: {len(table['table'].columns)}"
        })
        count = count+1

    return title_details
