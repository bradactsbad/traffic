#!/usr/bin/env python

import yaml
import requests
from bs4 import BeautifulSoup


def get_511(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    reports = soup.find_all('div', {'class': 'reportBody'})
    return [report.text.strip() for report in reports]

with open('urls.yaml', 'r') as urls_file:
    URLS = yaml.safe_load(urls_file)['urls']


if __name__ == "__main__":
    reports = []
    for url in URLS:
        reports += get_511(url)
    for report in reports:
        print(report + '\n')
