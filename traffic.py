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


def load_from_yaml():
    with open("urls.yaml", "r") as urls_file:
        URLS = yaml.safe_load(urls_file)["urls"]
    reports = []
    for url in URLS:
        reports += get_511(url)
    return reports


def parse_args():
    parser = argparse.ArgumentParser(
        prog="traffic", description="Virginia 511 compatible traffic scraper."
    )
    parser.add_argument(
        "location",
        nargs="?",
        default=None,
        help="optional, if not supplied returns all",
    )
    parser.add_argument("-b", "--bridge", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    reports = load_from_yaml()
    if args.bridge:
        reports = [report for report in reports if "Benjamin Harrison Bridge" in report]
    if args.location:
        reports = [report for report in reports if args.location in report]
    for report in reports:
        print(report + "\n")


if __name__ == "__main__":
    main()
