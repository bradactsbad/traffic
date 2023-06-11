#!/usr/bin/env python

import os
import requests
import argparse
from functools import reduce
from operator import concat
from concurrent import futures
from bs4 import BeautifulSoup


def get_511(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    reports = soup.find_all("div", {"class": "reportBody"})
    return [report.text.strip() for report in reports]


def load_urls_from_config():
    URLS_FILENAME = "urls.txt"

    def urls_filepath(filename):
        script_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(script_path, filename)

    with open(urls_filepath(URLS_FILENAME)) as f:
        urls = f.read().splitlines()
    return urls


def get_reports_from_urls(urls):
    reports = []
    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        reports = list(executor.map(get_511, urls))
    return reduce(concat, reports)


def cli():
    def parse_args():
        parser = argparse.ArgumentParser(
            prog="traffic", description="Virginia 511 compatible traffic scraper."
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
            "location",
            nargs="?",
            default=None,
            help="Find results including [location]. Case insensitive. Optional. If this and all options are empty, the program returns all data.",
        )
        return parser.parse_args()

    def print_output(output):
        if len(output) == 0:
            print("No results to display.")
        else:
            for i, line in enumerate(output):
                if i == len(output) - 1:
                    print(line)
                else:
                    print(line + "\n")

    def search(reports, *terms):
        results = []
        for term in terms:
            results += [report for report in reports if term.lower() in report.lower()]
        return results

    args = parse_args()
    reports = get_reports_from_urls(load_urls_from_config())
    output = []
    if args.bridge:
        TERM = "Benjamin Harrison Bridge"
        output += search(reports, TERM)
    if args.rt5:
        TERMS = ("rt. 5E/W", "VA-5")
        results = search(reports, *TERMS)
        if len(results) == 0:
            output += ["There are no results for VA-5 at this time."]
        else:
            output += results
    if args.location:
        output += search(args.location, reports)
    else:
        if not args.rt5 and not args.bridge:
            output = reports
    print_output(output)


if __name__ == "__main__":
    cli()
