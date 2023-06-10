#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

URL = "https://www.511virginia.org/mobile/?menu_id=Prince%20George%20County&ident=County%7CPrince%20George%20County"


def get_511(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    elements = (("h2", "reportHeading"), ("div", "reportBody"), ("h1", "reportType"))
    page_data = {}
    for i, e in enumerate(elements):
        page_data[e[1]] = (soup.find_all(e[0], {"class": e[1]}),)
    data = {}
    for (
        k,
        v,
    ) in page_data.items():
        for results in v:
            for tag in results:
                if k in data:
                    data[k].append(tag.text.strip())
                else:
                    data[k] = [tag.text.strip()]
    reports = []
    first_data = next(iter(data.items()))
    number_of_reports = len(first_data[1])
    for i in range(0, number_of_reports):
        reports.append(dict())
    for i, report in enumerate(reports):
        for key, content in data.items():
            report[key] = content[i]
    return reports


if __name__ == "__main__":
    reports = get_511(URL)
    for report in reports:
        print(report["reportBody"] + "\n")
