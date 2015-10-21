#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import csv
import re
import json
import datetime
from pyexcel.cookbook import merge_all_to_a_book
import pyexcel.ext.xlsx # needed to support xlsx format, pip install pyexcel-xlsx
import glob

def write_csv_header(file):
  f = open(file,'w')
  try:
    writer = csv.writer(f)
    writer.writerow( ('Реестровый номер',  'Полное наименование', 'Сокращенное наименование', 'Адрес (место нахождения)', 'Почтовый адрес', 'Адрес официального сайта в сети "Интернет"', 'ИНН', 'ОГРН', 'Членство туроператора, осуществления деятельности в области выездного туризма, в объединении туроператоров в сфере выездного туризма', 'Адреса структурных подразделений', 'Имя периода', 'Общий размер финансовой гарантии', 'Размер финансового обеспечения', 'Способ финансового обеспечения', 'Срок действия финансового обеспечения c', 'Срок действия финансового обеспечения по', 'Наименование организации, предоставившей финансовое обеспечение', 'Адрес (место нахождения) организации, предоставившей финансовое обеспечение', 'Почтовый адрес организации, предоставившей финансовое обеспечение', 'Номер приказа', 'Дата приказа', 'Номер выданного свидетельства') )
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

def csv_to_xls(cf,nf):
  merge_all_to_a_book(glob.glob(cf), nf)

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
      if info_about_financial_guarantee:
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
        if 'doc0' in documents:
          latest_document = documents['doc0']
          doc_financial_guarantee = latest_document['financial_guarantee']
          doc_way_of_financial_guarantee = latest_document['way_of_financial_guarantee']
          doc_start_date_of_financial_guarantee = latest_document['start_date_of_financial_guarantee']
          doc_end_date_of_financial_guarantee = latest_document['end_date_of_financial_guarantee']
          doc_entity_name = latest_document['entity_name']
          doc_entity_location_address = latest_document['entity_location_address']
          doc_entity_postal_address = latest_document['entity_postal_address']
        else:
          doc_financial_guarantee = doc_way_of_financial_guarantee = doc_start_date_of_financial_guarantee = doc_end_date_of_financial_guarantee = doc_entity_name = doc_entity_location_address = doc_entity_postal_address = 'None'

      forms_of_tourism_activities = item.get('E13')
      order_in_SFR = item.get('E14')
      if order_in_SFR:
        for key in order_in_SFR:
          number_of_order = order_in_SFR[key]
          date_of_order = order_in_SFR[key]
          issue_certificate_number = order_in_SFR[key]
      else:
          number_of_order = date_of_order = issue_certificate_number = 'None'
      for key in info_about_financial_guarantee[0]:
        tupl = (reg_number,full_name,abbreviated_name,address_location,postal_address,website,inn,ogrn,membership, structural_units_addresses,name_of_period,amount_of_financial_guarantee, doc_financial_guarantee,doc_way_of_financial_guarantee, doc_start_date_of_financial_guarantee, doc_end_date_of_financial_guarantee, doc_entity_name, doc_entity_location_address, doc_entity_postal_address, number_of_order, date_of_order, issue_certificate_number)
      tupl = [x.encode('utf-8').strip() for x in tupl]
      write_csv_body(file, tupl)
#    exit(1)

if __name__ == "__main__":
  list_url = 'http://opendata.russiatourism.ru/list.csv'
  structure_url = 'http://opendata.russiatourism.ru/7708550300-ReestrRosturizm1B/structure-20140904.json'
  out_file_csv = './generated.csv'
  out_file_xlsx = './generated.xlsx'

  st = get_content(structure_url).read()
  csvcontent = get_content(list_url)
  filenames = get_filenames(csvcontent)
  write_csv_header(out_file_csv)
  for fname in filenames:
    jsoncontent = get_json(fname)
    parse_json(jsoncontent, out_file_csv)

  csv_to_xls(out_file_csv,out_file_xlsx)
