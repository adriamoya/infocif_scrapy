# -*- coding: utf-8 -*-
import re
from argparse import ArgumentParser

def print_breakline():
    print()
    print('#'*80)
    print()


def numberize(s, dtype='int'):
    try:
        negative = re.search('-(?=\d)', s)
        if negative:
            return -1*int(''.join(re.findall('\d+', s)))
        else:
            return int(''.join(re.findall('\d+', s)))
    except:
        return None


def get_arguments():

    # Argument handling
    parser = ArgumentParser()
    parser.add_argument("--single-page", default=False, action="store_true", help="Scrape only one page (default all pages)")
    args = parser.parse_args()

    # Setting default values
    single_page = args.single_page

    print_breakline()

    # Single page scrapping
    if args.single_page:
        single_page = True
        print('---> Scrapping mode: Single page')
    else:
        print('---> Scrapping mode: All pages')

    print_breakline()

    return single_page
