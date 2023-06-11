#!/usr/bin/env python

import os
import yaml
import requests
import argparse
import re
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
    URLS_FILENAME = "urls.yaml"

    def urls_filepath(filename):
        script_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(script_path, filename)

    with open(urls_filepath(URLS_FILENAME), "r") as urls_file:
        return yaml.safe_load(urls_file)["urls"]


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
            "--rt5", action="store_true", help="Return available information on SR5."
        )
        parser.add_argument(
            "location",
            nargs="?",
            default=None,
            help="Search data for a location. Case insensitive. Optional; if this is empty along with all options, the program returns all data.",
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

    def search(terms, reports):
        def search_by_term(term, reports):
            return [report for report in reports if term.lower() in report.lower()]

        results = []
        if type(terms) is str:
            results += search_by_term(terms, reports)
        else:
            for term in terms:
                results += search_by_term(term, reports)
        return results

    args = parse_args()
    reports = get_reports_from_urls(load_urls_from_config())
    output = []
    if args.bridge:
        TERM = "Benjamin Harrison Bridge"
        output += search(TERM, reports)
    if args.rt5:
        TERMS = ("rt. 5E/W", "VA-5")
        results = search(TERMS, reports)
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
