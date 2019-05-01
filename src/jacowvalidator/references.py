import re
from itertools import chain


RE_REFS_LIST = re.compile(r'^\[([\d]+)\]')
RE_REFS_LIST_TAB = re.compile(r'^\[([\d]+)\]\t')
RE_REFS_INTEXT = re.compile(r'(?<!^)\[([\d ,-]+)\]')


def _ref_to_int(ref):
    try:
        return [int(ref)]
    except ValueError:
        if ',' in ref:
            return list(
                chain.from_iterable(_ref_to_int(i) for i in ref.split(',') if i.strip())
            )
        elif '-' in ref:
            return list(range(*(int(v) + i for i, v in enumerate(ref.split('-')))))
        raise


def extract_references(doc):
    data = iter(doc.paragraphs)
    references_in_text = []

    # don't start looking until abstract header
    for p in data:
        if p.text.strip().lower() == 'abstract':
            break
    else:
        raise Exception('Abstract header not found')

    # find all references in text and references list
    references_list = []
    ref_list_start = 0
    for i, p in enumerate(data):
        for ref in RE_REFS_INTEXT.findall(p.text):
            references_in_text.append(_ref_to_int(ref))

        refs = RE_REFS_LIST.findall(p.text.strip())
        if refs:
            for ref in refs:
                if int(ref) == 1:
                    ref_list_start = i
                references_list.append(
                    dict(id=int(ref), text=p.text.strip(), style=p.style.name)
                )
        elif ref_list_start > 0:
            should_find = references_list[-1]['id'] + 1
            if str(should_find) in p.text.strip()[:4]: # only look in first 4 chars
                references_list.append(
                    dict(id=should_find, text=p.text.strip(), style=p.style.name, text_error=f"Number format wrong should be [{should_find}]")
                )

    # check references in body are in correct order
    stack = [0]
    seen = []
    out_of_order = set()
    for _range in references_in_text:
        for _ref in _range:
            if _ref in stack:
                continue
            if _ref - stack[-1] == 1:
                stack.append(_ref)
            elif _ref not in seen:
                seen.append(_ref)
        for _ref in seen.copy():
            if _ref - stack[-1] == 1:
                stack.append(_ref)
                seen.remove(_ref)
        if len(seen) > 0:
            out_of_order.update(seen)

    # get a set of references so we know which ones are used
    used_references = set(chain.from_iterable(references_in_text))

    # check reference styles, order etc
    ref_count = len(references_list)
    seen = set()
    for i, ref in enumerate(references_list, 1):
        if ref['id'] in seen:
            ref['duplicate'] = True
        seen.add(ref['id'])
        ref['order_ok'] = i == ref['id'] and i not in out_of_order
        ref['used'] = i in used_references

        if not RE_REFS_LIST_TAB.search(ref['text']):
            ref['text_error'] = f"Number format error should be [{i}] followed by a tab"

        if ref_count <= 9:
            ref['style_ok'] = ref['style'] == 'JACoW_Reference when <= 9 Refs'
        else:
            if i <= 9:
                ref['style_ok'] = ref['style'] == 'JACoW_Reference #1-9 when >= 10 Refs'
            else:
                ref['style_ok'] = ref['style'] == 'JACoW_Reference #10 onwards'

    return references_in_text, references_list
