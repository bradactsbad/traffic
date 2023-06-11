#!/usr/bin/env python

import yaml
import requests
import argparse
from bs4 import BeautifulSoup


def get_511(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    reports = soup.find_all("div", {"class": "reportBody"})
    return [report.text.strip() for report in reports]


def load_reports_from_config():
    with open("urls.yaml", "r") as urls_file:
        URLS = yaml.safe_load(urls_file)["urls"]
    reports = []
    for url in URLS:
        reports += get_511(url)
    return reports


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
        for line in output:
            print(line + "\n")

    def search(term, reports):
        return [report for report in reports if term.lower() in report.lower()]

    args = parse_args()
    reports = load_reports_from_config()
    output = []
    if args.bridge:
        TERM = "Benjamin Harrison Bridge"
        output += search(TERM, reports)
    if args.rt5:
        TERM = "rt. 5E/W"
        output += search(TERM, reports)
    if args.location:
        output += search(args.location, reports)
    else:
        if not args.rt5 and not args.bridge:
            output = reports
    print_output(output)


if __name__ == "__main__":
    cli()
