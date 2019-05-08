import re


def get_author_list(text):
    """function to extract authors from some text that will also include
    associations

    example input:

    `J. C. Jan†, F. Y. Lin, Y. L. Chu, C. Y. Kuo, C. C. Chang, J. C. Huang and C. S. Hwang,
National Synchrotron Radiation Research Center, Hsinchu, Taiwan, R.O.C`

    or

    `M.B. Behtouei, M. Migliorati, L. Palumbo, B. Spataro, L. Faillace`

    assumptions:

    - if you split by ', ' and the second character of a token is a '.' period
        then its probably a valid token (an author) but this is not guaranteed
        (see above example that ends in 'R.O.C')

    - There can be multiple initials as evidenced above.

    - Initials may not necessarily be split by a space.

    watch out for:

    - hypenated names: 'B. Walasek-Hoehne'
    - hyphenated initials: 'E. J-M. Voutier' 'J.-L. Vay'
    - multiple surnames: 'M.J. de Loos' 'S.B. van der Geer' 'A. Martinez de la Ossa' 'N. Blaskovic Kraljevic' 'G. Guillermo Cant�n' 'C. Boscolo Meneguolo'
    - surname with apostrophes: 'G. D'Alessandro'
    - extra stuff tacked on: 'S.X. Zheng [on leave]' 'G.R. Li [on leave]' (from the csv file)
    - one rare instance of non-period separated initials: 'Ph. Richerot (from csv file)

    my pattern of a name which should match vast majority of names while not matching vast majority of non-names:
    single letter, followed by a period, potentially followed by a space but
    not always, repeated n times, and ending in a word of more than one character
    which may contain hyphens, apostrophes, repeated n times, and finally
    finishing with a comma

    word character followed by dot and potentially space, repeated n times
    then
    word character repeated n times

    /(\\w\\.\\ ?)+(\\w+\\ ?)+/g   (note this comment had to double up the escape backslashes)

    (https://regexr.com/)

    """
    potential_authors = text.replace(' and ', ', ').split(', ')
    filtered_authors = list()
    my_name_pattern = re.compile("(-?\\w\\.\\ ?)+([\\w]{2,}\\ ?)+")
    # the allowance of an optional hyphen preceding an initial is to satisfy a
    # common pattern observed with the papers coming out of asia.
    for author in potential_authors:
        if my_name_pattern.match(author):   # match has an implied ^ at the start
            # which is ok for our purposes.
            filtered_authors.append(author)
    return filtered_authors
