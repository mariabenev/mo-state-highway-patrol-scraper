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

    incident_nums = set()

    for tr in tr_all:
        url = tr.td.a.attrs['href']
        incident_num = url.split('ACC_RPT_NUM=')[1].strip()
        incident_nums.add(incident_num)

    return incident_nums


def get_incident_report(incident_num):

    url = 'https://www.mshp.dps.missouri.gov/HP68/AccidentDetailsAction'

    params = {'ACC_RPT_NUM': incident_num}

    r = requests.get(url, params=params, headers=HEADERS)

    r.raise_for_status()

    return r.content

def extract_report_tables(incident_report):

	soup = BeautifulSoup(incident_report, 'html5lib')

	tables = soup.find_all('table')

	return tables

def extract_report_headers(table):

	th_all = table.find_all('th')

	headers = ['incident_number']

	for th in th_all:
		header = th.text.strip().replace(" ", "_").replace("/", '_').lower()
		headers.append(header)

	return headers

def extract_report_rows(table, num):

	tbody = table.find('tbody')

	tr_all = tbody.find_all('tr')

	rows = []

	for tr in tr_all:
		row = [num]
		for td in tr.find_all('td'):
			row.append(td.text.strip())
		rows.append(row)

	return rows

def extract_table_data(table, num):
	headers = extract_report_headers(table)
	rows = extract_report_rows(table, num)
	data = []
	for row in rows:
		dictionary = dict(zip(headers, row))
		data.append(dictionary)
	
	return data

def extract_crash_headers(table):
	th_all = table.find_all('th')

	headers = []

	for th in th_all:
		header = th.text.strip().replace(" ", "_").replace("/", '_').lower()
		headers.append(header)
	headers.append('misc_information')

	return headers

def extract_crash_rows (table, misc):
	tbody = table.find('tbody')

	tr_all = tbody.find_all('tr')

	rows = []

	for tr in tr_all:
		row = []
		for td in tr.find_all('td'):
			row.append(td.text.strip())
		row.append(misc)
		rows.append(row)

	return rows

def extract_crash_data(table, misc):
	headers = extract_crash_headers(table)
	rows = extract_crash_rows(table, misc)
	data = []
	for row in rows:
		dictionary = dict(zip(headers, row))
		data.append(dictionary)
	
	return data

def extract_misc_rows(table):

	tbody = table.find('tbody')

	tr = tbody.find('tr')

	td = tr.find('td')

	return td.text.strip()

def main():
	all_crashes = []
	all_vehicles = []
	all_injuries = []
	injury_types = get_injury_types()

	for injury_type in injury_types:
		search_results = get_search_results(injury_type)
		incident_nums = extract_incident_nums(search_results)

		for num in list(incident_nums):
			incident_report = get_incident_report(num)
			tables = extract_report_tables(incident_report)
			vehicle_headers = extract_report_headers(tables[1])
			injury_headers = extract_report_headers(tables[2])
			misc = extract_misc_rows(tables[3])
			crashes = extract_crash_data(tables[0], misc)
			vehicles = extract_table_data(tables[1], num)
			injuries = extract_table_data(tables[2], num)
			all_crashes.append(crashes)
			all_vehicles.append(vehicles)
			all_injuries.append(injuries)

			sleep(3)

	

	with open('all_crashes.csv', 'w', newline='') as csvfile:
		headers = ['investigated_by', 'incident#', 'gps_latitude', 'gps_longitude', 'date', 'time', 'county', 'location', 'troop', 'misc_information']
		writer = csv.DictWriter(csvfile, fieldnames=headers)
		writer.writeheader()

		for rows in all_crashes:
			for row in rows:
				writer.writerow(row)

	with open('all_vehicles.csv', 'w', newline='') as csvfile:
		headers = vehicle_headers
		writer = csv.DictWriter(csvfile, fieldnames=headers)
		writer.writeheader()

		for rows in all_vehicles:
			for row in rows:
				writer.writerow(row)

	with open('all_injuries.csv', 'w', newline='') as csvfile:
		headers = injury_headers
		writer = csv.DictWriter(csvfile, fieldnames=headers)
		writer.writeheader()

		for rows in all_injuries:
			for row in rows:
				writer.writerow(row)

	

if __name__ == '__main__':
    main()
