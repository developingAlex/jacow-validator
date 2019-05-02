from jacowvalidator.authors import get_author_list


def test_simple_author_extraction():
    PLAIN_SIX_AUTHOR_EXAMPLE = "E.J. Lee, M.G. Hur, J.H. Park, S.D. Yang, Y.B. Kong, H.S. Song"
    list = get_author_list(PLAIN_SIX_AUTHOR_EXAMPLE)
    assert len(list) == 6


def test_multi_surname_extraction():
    MULTI_SURNAME_EXAMPLE = "J.G.R.S.Franco James, R.Junqueira"
    list = get_author_list(MULTI_SURNAME_EXAMPLE)
    assert len(list) == 2


def test_nonascii_surname_extraction():
    NONASCII_SURNAME_EXAMPLE = "S.R. Marques, A.R.D. Rodrigues, C. Rodrigues, F. Rodrigue, F.H. de S�"
    list = get_author_list(NONASCII_SURNAME_EXAMPLE)
    assert len(list) == 5


def test_affiliations_not_extracted():
    NONASCII_SURNAME_EXAMPLE = "C. C. Chang, J. C. Huang, C. S. Hwang, \n\
    National Synchrotron Radiation Research Center, Hsinchu, Taiwan, R.O.C"
    list = get_author_list(NONASCII_SURNAME_EXAMPLE)
    assert len(list) == 3
    assert 'R.O.C' not in list
    assert 'C. C. Chang' in list
    assert 'J. C. Huang' in list
    assert 'C. S. Hwang' in list


def test_linking_word_and_is_parsed():
    AND_SEPARATED_EXAMPLE = "C. C. Chang, J. C. Huang and C. S. Hwang, \n\
    National Synchrotron Radiation Research Center, Hsinchu, Taiwan, R.O.C"
    list = get_author_list(AND_SEPARATED_EXAMPLE)
    assert len(list) == 3
    assert 'R.O.C' not in list
    assert 'C. C. Chang' in list
    assert 'J. C. Huang' in list
    assert 'C. S. Hwang' in list

#
# def test_footnote_chars_removed():
#     FOOTNOTE_SYMBOL_EXAMPLE = "J. C. Jan†, F. Y. Lin,"
#     list = get_author_list(FOOTNOTE_SYMBOL_EXAMPLE)
#     assert len(list) == 2
#     assert 'J. C. Jan' in list
#     assert 'F. Y. Lin' in list
