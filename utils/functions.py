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
    parser.add_argument("-s", dest="start_page", default=1, help="Start page (default=1)")
    parser.add_argument("-e", dest="end_page", default=596, help="End page (default=596)")
    parser.add_argument("--single-page", default=False, action="store_true", help="Scrape only one page (default all pages)")
    args = parser.parse_args()

    # Setting default values
    start_page  = args.start_page
    end_page    = args.end_page
    single_page = args.single_page

    print_breakline()

    # Start-page
    if args.start_page:
        try:
            start_page = int(args.start_page)
            print('---> Start page: \t#%s' % start_page)
        except:
            raise TypeError('Integer expected for page argument')

    # End-page
    if args.end_page:
        try:
            end_page = int(args.end_page)
            print('---> End page: \t\t#%s' % end_page)
        except:
            raise TypeError('Integer expected for page argument')

    # Single page scrapping
    if args.single_page:
        single_page = True
        print('---> Scrapping mode: \tOnly page #%s' % start_page)
    else:
        if end_page:
            print('---> Scrapping mode: \tAll pages between #%s and #%s' % (start_page, end_page))
        else:
            print('---> Scrapping mode: \tAll pages from #%s onwards' % start_page)

    print_breakline()

    return start_page, end_page, single_page
