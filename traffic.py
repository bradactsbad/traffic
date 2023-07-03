#!/usr/bin/env python

import os
import urllib.request
import argparse
from functools import reduce
from operator import concat
from concurrent import futures
from bs4 import BeautifulSoup

URLS = """https://www.511virginia.org/mobile/?menu_id=Henrico%20County&ident=County%7CHenrico%20County
https://www.511virginia.org/mobile/?menu_id=Prince%20George%20County&ident=County%7CPrince%20George%20County
https://www.511virginia.org/mobile/?menu_id=Richmond&ident=City%7CRichmond
https://www.511virginia.org/mobile/?menu_id=New%20Kent%20County&ident=County%7CNew%20Kent%20County
https://www.511virginia.org/mobile/?menu_id=Chesterfield%20County&ident=County%7CChesterfield%20County"""


def fetch():
    def fetch(url):
        with urllib.request.urlopen(url) as resp:
            soup = BeautifulSoup(resp, "xml")
        reports = soup.find_all("div", {"class": "reportBody"})
        return [report.text.strip() for report in reports]

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        reports = list(executor.map(fetch, URLS.splitlines()))
    return reduce(concat, reports)


def search(reports, *terms):
    results = []
    for term in terms:
        results += [rep for rep in reports if term.lower() in rep.lower()]  # type: ignore
    return results


def main():
    parser = argparse.ArgumentParser(
        prog="traffic", description="Virginia 511 road information."
    )
    parser.add_argument(
        "--bridge",
        action="store_true",
        help="Return available information on the Benjamin Harrison bridge.",
    )
    parser.add_argument(
        "--rt5", action="store_true", help="Return available information on VA-5."
    )
    parser.add_argument(
        "search",
        nargs="?",
        default=None,
        help="Find results including [search]. Case insensitive. Optional. If this and all options are empty, the program returns all data.",
    )
    args = parser.parse_args()
    output = []
    reports = fetch()
    if args.bridge:
        output += search(reports, "Benjamin Harrison Bridge")
    if args.rt5:
        results = search(reports, *("rt. 5E/W", "VA-5"))
        if len(results) == 0:
            output += ["There are no results for VA-5 at this time."]
        else:
            output += results
    if args.search:
        output += search(reports, args.search)
    else:
        if not any((args.rt5, args.bridge)):
            output = reports
    if len(output) == 0:
        print("No results to display.")
    else:
        for i, line in enumerate(output):
            if i == len(output) - 1:
                print(line)
            else:
                print(line + "\n")  # type: ignore


if __name__ == "__main__":
    main()
