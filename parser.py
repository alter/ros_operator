#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import csv
import re
import json
import datetime

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
  url = "http://opendata.russiatourism.ru/%s/data-%s-structure-20140904.json" % (fname, date)
  print url
  response = get_content(url).read()
  return response

def parse_json(jsoncontent):
  jlist = json.loads(jsoncontent)
  if jlist:
    for item in jlist:
      reg_number = item.get('E1')
      full_name = item.get('E2')
      abbreviated_name = item.get('E3')
      address_location = item.get('E4')
      postal_address = item.get('E5')
      website = item.get('E6')
      inn = item.get('E7')
      ogrn = item.get('E8')
      membership = item.get('E9')
      structural_units_addresses = item.get('E10')
      total_amount_of_funds = item.get('E11')
      info_about_financial_guarantee = item.get('E12')
      name_of_period = info_about_financial_guarantee[0].get('E12A')
      amount_of_financial_guarantee = info_about_financial_guarantee[0].get('E12B')
      list_of_documents = info_about_financial_guarantee[0].get('E12C')
      documents = {}
      for idx, item in enumerate(list_of_documents):
        documents['doc'+str(idx)] = {
          'financial_guarantee': item.get('E12C1'),
          'way_of_financial_guarantee': item.get('E12C2'),
          'number_of_doc': item.get('E12C3'),
          'date_of_doc': item.get('E12C4'),
          'start_date_of_financial_guarantee': item.get('E12C5'),
          'end_date_of_financial_guarantee': item.get('E12C6'),
          'entity_name': item.get('E12C7'),
          'entity_location_address': item.get('E12C8'),
          'entity_postal_address': item.get('E12C9')
        }
      forms_of_tourism_activities = item.get('E13')
      order_in_SFR = item.get('E14')
      print info_about_financial_guarantee[0]
      string = u"%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %(reg_number,full_name,abbreviated_name,address_location,postal_address,website,inn,ogrn,membership,structural_units_addresses,total_amount_of_funds,info_about_financial_guarantee,name_of_period,amount_of_financial_guarantee,list_of_documents)
      csv = u''.join(string).encode('utf-8').strip()
      f = open("/tmp/1.csv", "w")  
      f.write(csv)
      f.close()
      exit(1)

if __name__ == "__main__":
  list_url = 'http://opendata.russiatourism.ru/list.csv'
  structure_url = 'http://opendata.russiatourism.ru/7708550300-ReestrRosturizm1B/structure-20140904.json'

  st = get_content(structure_url).read()
  csvcontent = get_content(list_url)
  filenames = get_filenames(csvcontent)
  for fname in filenames:
    jsoncontent = get_json(fname)
    parse_json(jsoncontent)

