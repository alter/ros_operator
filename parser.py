#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import csv
import re
import json
import datetime

def write_csv_header(file):
  f = open(file,'w')
  try:
    writer = csv.writer(f)
    writer.writerow( ('Реестровый номер',  'Полное наименование', 'Сокращенное наименование', 'Адрес (место нахождения)', 'Почтовый адрес', 'Адрес официального сайта в сети "Интернет"', 'ИНН', 'ОГРН', 'Членство туроператора, осуществления деятельности в области выездного туризма, в объединении туроператоров в сфере выездного туризма', 'Адреса структурных подразделений', 'Общий размер финансового обеспечения') )
  finally:
    f.close()

def write_csv_body(file, data):
  f = open(file,'a')
  try:
    writer = csv.writer(f)
    writer.writerow(data)
  finally:
    f.close()

def get_date():
  return datetime.datetime.now().strftime("%Y%m%d")

def get_content(url):
  response = urllib2.urlopen(url)
  return response

def get_filenames(csvcontent):
  filenames = []
  reader = csv.reader(csvcontent)
  pattern = '^7708550300-ReestrRosturizm[0-9]*B$'
  prog = re.compile(pattern)
  for row in reader:
    result = prog.match(row[0])
    if result:
      filenames.append(row[0])
  return filenames

def get_json(fname):
  date = get_date()
  #date = 20151020
  url = "http://opendata.russiatourism.ru/%s/data-%s-structure-20140904.json" % (fname, date)
  response = get_content(url).read()
  return response

def parse_json(jsoncontent, file):
  jlist = json.loads(jsoncontent)
  if jlist:
    for item in jlist:
      reg_number = item.get('E1').replace('\n','|')
      full_name = item.get('E2').replace('\n','|')
      abbreviated_name = item.get('E3').replace('\n','|')
      address_location = item.get('E4').replace('\r\n','|').replace('\n', '|')
      postal_address = item.get('E5').replace('\r\n','|').replace('\n', '|')
      website = item.get('E6').replace('\n','|')
      inn = item.get('E7').replace('\n','|')
      ogrn = item.get('E8').replace('\n','|')
      membership = item.get('E9').replace('\n','|')
      structural_units_addresses = item.get('E10').replace('\r\n','|').replace('\n', '|')
      total_amount_of_funds = item.get('E11').replace('\n','|')
      info_about_financial_guarantee = item.get('E12')
      name_of_period = info_about_financial_guarantee[0].get('E12A').replace('\n','|')
      amount_of_financial_guarantee = info_about_financial_guarantee[0].get('E12B').replace('\n','|')
      list_of_documents = info_about_financial_guarantee[0].get('E12C')
      documents = {}
      for idx, item in enumerate(list_of_documents):
        documents['doc'+str(idx)] = {
          'financial_guarantee': item.get('E12C1').replace('\n','|'),
          'way_of_financial_guarantee': item.get('E12C2').replace('\n','|'),
          'number_of_doc': item.get('E12C3').replace('\n','|'),
          'date_of_doc': item.get('E12C4').replace('\n','|'),
          'start_date_of_financial_guarantee': item.get('E12C5').replace('\n','|'),
          'end_date_of_financial_guarantee': item.get('E12C6').replace('\n','|'),
          'entity_name': item.get('E12C7').replace('\n','|'),
          'entity_location_address': item.get('E12C8').replace('\n','|'),
          'entity_postal_address': item.get('E12C9').replace('\n','|')
        }
      forms_of_tourism_activities = item.get('E13')
      order_in_SFR = item.get('E14')
      for key in info_about_financial_guarantee[0]:
        print info_about_financial_guarantee[0][key]
      tupl = (reg_number.encode('utf-8').strip(),full_name.encode('utf-8').strip(),abbreviated_name.encode('utf-8').strip(),address_location.encode('utf-8').strip(),postal_address.encode('utf-8').strip(),website.encode('utf-8').strip(),inn.encode('utf-8').strip(),ogrn.encode('utf-8').strip(),membership.encode('utf-8').strip(), structural_units_addresses.encode('utf-8').strip(),total_amount_of_funds.encode('utf-8').strip())
#      csv = u''.join(string).encode('utf-8').strip()
      write_csv_body(file, tupl)
    exit(1)

if __name__ == "__main__":
  list_url = 'http://opendata.russiatourism.ru/list.csv'
  structure_url = 'http://opendata.russiatourism.ru/7708550300-ReestrRosturizm1B/structure-20140904.json'
  out_file = './generated.csv'

  st = get_content(structure_url).read()
  csvcontent = get_content(list_url)
  filenames = get_filenames(csvcontent)
  write_csv_header(out_file)
  for fname in filenames:
    jsoncontent = get_json(fname)
    parse_json(jsoncontent, out_file)

