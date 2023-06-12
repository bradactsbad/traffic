#!/usr/bin/env python

import os
import requests
import argparse
from functools import reduce
from operator import concat
from concurrent import futures
from bs4 import BeautifulSoup


class Traffic:
    URLS_FILENAME = "urls.txt"

    def __init__(self):
        self.urls = self._load_urls_from_config()
        self.reports = self._get_reports_from_urls()

    @staticmethod
    def get_511(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "xml")
        reports = soup.find_all("div", {"class": "reportBody"})
        return [report.text.strip() for report in reports]

    def _load_urls_from_config(self):
        def urls_filepath(filename):
            script_path = os.path.dirname(os.path.realpath(__file__))
            return os.path.join(script_path, filename)

        with open(urls_filepath(Traffic.URLS_FILENAME)) as f:
            urls = f.read().splitlines()
        return urls

    def _get_reports_from_urls(self):
        reports = []
        with futures.ThreadPoolExecutor(max_workers=8) as executor:
            reports = list(executor.map(self.get_511, self.urls))
        return reduce(concat, reports)

    def search(self, *terms):
        results = []
        for term in terms:
            results += [report for report in self.reports if term.lower() in report.lower()]  # type: ignore
        return results


class Cli:
    def __init__(self, traffic):
        self.output = []
        self.traffic = traffic
        self.args = self.parse_args()
        if self.args.bridge:
            self.bridge()
        if self.args.rt5:
            self.rt5()
        if self.args.search:
            self.search()
        else:
            if not any((self.args.rt5, self.args.bridge)):
                self.output = self.traffic.reports
        self.print_output()

    def search(self):
        self.output += self.traffic.search(self.args.search)

    @staticmethod
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
            "search",
            nargs="?",
            default=None,
            help="Find results including [search]. Case insensitive. Optional. If this and all options are empty, the program returns all data.",
        )
        return parser.parse_args()

    def bridge(self):
        TERM = "Benjamin Harrison Bridge"
        self.output += self.traffic.search(TERM)

    def rt5(self):
        TERMS = ("rt. 5E/W", "VA-5")
        results = self.traffic.search(*TERMS)
        if len(results) == 0:
            self.output += ["There are no results for VA-5 at this time."]
        else:
            self.output += results

    def print_output(self):
        if len(self.output) == 0:
            print("No results to display.")
        else:
            for i, line in enumerate(self.output):
                if i == len(self.output) - 1:
                    print(line)
                else:
                    print(line + "\n")


if __name__ == "__main__":
    Cli(Traffic())
