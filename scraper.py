#!/usr/bin/env python
# coding: utf-8
from bs4 import BeautifulSoup
from datetime import timedelta
import requests
import requests_cache
from time import sleep
from models import Crash, Vehicle, Injury
from peewee import DoesNotExist


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


def extract_incident_nums(search_results):
    soup = BeautifulSoup(search_results, 'lxml')

    incident_nums = set()

    table = soup.find('table', class_='accidentOutput')

    td_all = table.find_all('td', class_='infoCellPrint')

    for td in td_all:
        url = td.find('a').attrs['href']
        incident_num = url.split('=')[1].strip()
        incident_nums.add(incident_num)

    return incident_nums


def get_incident_report(incident_num):

    url = 'https://www.mshp.dps.missouri.gov/HP68/AccidentDetailsAction'

    r = requests.get(
        url, params={'ACC_RPT_NUM': incident_num}
    )

    r.raise_for_status()

    return r.content


def get_incident_report_tables(incident_report):
    soup = BeautifulSoup(incident_report, 'lxml')

    return soup.find_all('table', class_='accidentOutput')    


def extract_crash_data(crash_info_table, misc_info_table):

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


def extract_vehicle_data(incident_num, table):
    rows = table.find_all('tr')[1:]

    for row in rows:
        cells = row.find_all('td', class_='infoCell3')

        Vehicle.create(
            incident_num=incident_num,
            vehicle_num=cells[0].text.strip(),
            description=cells[1].text.strip(),
            damage=cells[2].text.strip(),
            disposition=cells[3].text.strip(),
            driver_name=cells[4].text.strip(),
            driver_gender=cells[5].text.strip(),
            driver_age=cells[6].text.strip(),
            safety_device=cells[7].text.strip(),
            driver_city_state=cells[8].text.strip(),
            driver_insurance=cells[9].text.strip(),
            direction=cells[10].text.strip(),
        )


def extract_injury_data(incident_num, table):
    rows = table.find_all('tr')[1:]

    for row in rows:
        cells = row.find_all('td', class_='infoCell3')

        Injury.create(
            incident_num=incident_num,
            vehicle_num=cells[0].text.strip(),
            name=cells[1].text.strip(),
            gender=cells[2].text.strip(),
            age=cells[3].text.strip(),
            injury_type=cells[4].text.strip(),
            safety_device=cells[5].text.strip(),
            city_state=cells[6].text.strip(),
            involvement=cells[7].text.strip(),
            disposition=cells[8].text.strip(),
        )


def main():
    for injury_type in get_injury_types():
        search_results = get_search_results(injury_type)
        incident_nums = extract_incident_nums(search_results)

        for incident_num in incident_nums:
            print('checking for %s' % incident_num)
            try:
                Crash.get(incident_num=incident_num)
            except DoesNotExist:
                print('extracting data for %s' % incident_num)
                incident_report = get_incident_report(incident_num)
                tables = get_incident_report_tables(incident_report)
                extract_crash_data(tables[0], tables[3])
                extract_vehicle_data(incident_num, tables[1])
                extract_injury_data(incident_num, tables[2])
                print('done')
                sleep(3)
            else:
                print('%s already exists' % incident_num)

        sleep(3)
        # TODO: don't sleep if prev request came from cache


if __name__ == '__main__':
    main()
