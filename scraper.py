#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import csv
from time import sleep


SEARCH_URL = "https://www.mshp.dps.missouri.gov/HP68/SearchAction"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0'
    }


def get_injury_types():
    r = requests.get(SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    options = soup.find('select', id='injuryType') \
        .find_all('option')

    injury_types = [
        o.attrs['value'] for o in options if len(o.attrs['value']) > 0
    ]

    return injury_types


def get_search_results(injury_type):
    data = {'searchInjury': injury_type}
    r = requests.post(SEARCH_URL, headers=HEADERS, data=data)

    r.raise_for_status()

    return r.content


def extract_incident_nums(search_results):
    soup = BeautifulSoup(search_results, 'html.parser')

    table = soup.find('table')

    tr_all = table.find_all('tr')[1:]

    incident_nums = []

    for tr in tr_all:
        url = tr.td.a.attrs['href']
        incident_num = url.split('ACC_RPT_NUM=')[1].strip()
        incident_nums.append(incident_num)

    return incident_nums


def get_incident_report(incident_num):

    url = 'https://www.mshp.dps.missouri.gov/HP68/AccidentDetailsAction'

    params = {'ACC_RPT_NUM': incident_num}

    r = requests.get(url, params=params, headers=HEADERS)

    r.raise_for_status()

    return r.content


def main():
    injury_types = get_injury_types()

    for injury_type in injury_types[:1]:
        search_results = get_search_results(injury_type)
        incident_nums = extract_incident_nums(search_results)
        
        for num in incident_nums[:5]:
            incident_report = get_incident_report(num)

            print(incident_report)
            print('---------------------------------')

            sleep(3)


if __name__ == '__main__':
    main()
