#!/usr/bin/env python
# coding: utf-8
from bs4 import BeautifulSoup
from datetime import timedelta
import requests
import requests_cache
from time import sleep
from models import Crash


requests_cache.install_cache(
    'cache',
    expire_after=timedelta(hours=24),
    allowable_methods=('GET', 'POST')
)


SEARCH_URL = 'https://www.mshp.dps.missouri.gov/HP68/SearchAction'


def get_injury_types():
    r = requests.get(SEARCH_URL)
    soup = BeautifulSoup(r.content, 'lxml')

    options = soup.find('select', id='injuryType').find_all('option')

    injury_types = []

    for opt in options:
        value = opt.attrs['value']
        if len(value) > 0:
            injury_types.append(value)

    return injury_types


def get_search_results(injury_type):
    r = requests.post(
        SEARCH_URL,
        data={'searchInjury': injury_type}
    )

    r.raise_for_status()

    return r.content


def extract_incident_urls(search_results):
    soup = BeautifulSoup(search_results, 'lxml')

    incident_urls = set()

    table = soup.find('table', class_='accidentOutput')

    td_all = table.find_all('td', class_='infoCellPrint')

    for td in td_all:
        url = td.find('a').attrs['href']
        incident_urls.add(url)

    return incident_urls


def get_incident_report(rel_url):

    full_url = 'https://www.mshp.dps.missouri.gov/' + rel_url

    r = requests.get(full_url)

    r.raise_for_status()

    return r.content


def extract_incident_data(incident_report):
    soup = BeautifulSoup(incident_report, 'lxml')

    tables = soup.find_all('table', class_='accidentOutput')

    crash_info_table = tables[0]
    misc_info_table = tables[3]

    crash_info_cells = crash_info_table.find_all(
        'td', class_='infoCell3'
    )
    misc_info_cell = misc_info_table.find('span', id='Misc')

    crash = Crash.create(
        incident_num=crash_info_cells[1].text.strip(),
        investigated_by=crash_info_cells[0].text.strip(),
        gps_latitude=crash_info_cells[2].text.strip(),
        gps_longitude=crash_info_cells[3].text.strip(),
        date=crash_info_cells[4].text.strip(),
        time=crash_info_cells[5].text.strip(),
        county=crash_info_cells[6].text.strip(),
        location=crash_info_cells[7].text.strip(),
        troop=crash_info_cells[8].text.strip(),
        misc_info=misc_info_cell.text.strip(),
    )


def main():
    for injury_type in get_injury_types():
        search_results = get_search_results(injury_type)
        urls = extract_incident_urls(search_results)

        for url in urls:
            print('extracting data for %s' % url)
            incident_report = get_incident_report(url)
            extract_incident_data(incident_report)
            print('data for %s' % url)
            sleep(3)

        sleep(3)


if __name__ == '__main__':
    main()
