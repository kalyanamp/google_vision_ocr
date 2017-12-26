import json
from datetime import datetime as dt
import datetime
import sys

import re
sys.path.insert(0, '../image_processing')
import Common


class Paystub_details:
    def __init__(self):
        self.pay_frequency = ''
        self.employment_Start_date=datetime
        self.date_val = []
        self.date = []
        self.actual_date = []
        self.date_val1 = []
        self.zip_code=[]
        self.data, self.data1,self.value2 = [], [],[]
        self.c = Common.Common()
        with open('../config/city.json', 'r') as data_file:
            self.cities = json.load(data_file)

    def get_paystub_Address(self,value):
            try:
                zip_code = []
                text = ''.join(map(str, value))
                all_number = re.findall(
                    r"\s?\d{2,3}\w?\s\w+\,?|\s\d{3}\s\d{1}|\s\d{4}\s|\w*\s\d{5}\s\w*|\w*\s\d{5}-\d{4}|\w*\s\d{5}"
                    r"|\d{2}\s\w*|\w{2}\s\d{3}\s\d{2}|\w*\s\d{3}\s\d{1}\s\d{1}"
                    r"|\w*\s\d{4}-\d{4}|\w*\s\d{2,5}\s\d{2,3}-\d{4}|\w*\s\d{2,5}\s\d{2,3}",
                    text)
                number_val = ' '.join(map(str, all_number))

                data = re.findall(
                    r"\b((?=AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI"
                    r"|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN"
                    r"|TX|UT|VT|VI|VA|WA|WV|WI|WY)[A-Z]{2}[, ])(\d{5}(?:-\d{4})?|\d{4}(?:-\d{4})?)", number_val)
                for item in data:
                    zip_code.append("".join(item))
                print(zip_code)
                if zip_code != []:
                    if re.search(r'\w*\s(?=ID\s\d)', number_val):
                        code = zip_code[1]
                    else:
                        code = zip_code[0]
                    if re.match(r"\d{2,3}\s\w+\,", number_val):
                        street = ''.join(map(str, number_val.split(code, 1)[0].split()[-4]))
                    else:
                        street = ''.join(map(str, number_val.split(code, 1)[0].split()[-2]))
                    state_zip = code.split()
                    state = state_zip[0]
                    zipcode = state_zip[1]
                    city = ' '.join(map(str, number_val.split(code[0], 1)[0].split()[-2:]))
                    print("street", street)
                    full_address = self.c.find_between_r(text, street, city)
                    for i in range(len(self.cities['city'])):
                        # print(self.cities['city'][i])
                        if self.cities['city'][i].lower() in city.lower():
                            city = self.cities['city'][i]
                    return street, state, zipcode, city
            except Exception as E:
                full_address, street = None, None
                return full_address, street
    def get_paystub_name(self,value,street):
        try:
            print("in paystub",value)
            name = ' '.join(map(str, value.split(street, 1)[0].split()[-6:]))
            print("name", name)
            name_regex = re.findall(r'[A-Za-z]\w*\b', name)
            actual_name = " ".join(map(str, name_regex))
            actual_name = actual_name.replace('JTD', "")
            actual_name = actual_name.replace('AP', "")
            actual_name = actual_name.replace('Expires', "")
            actual_name = actual_name.replace('Name', "")
            actual_name = actual_name.replace('DENONE', "")
            actual_name = actual_name.replace('NONE', "")
            actual_name = actual_name.replace('Address', "")
            actual_name = actual_name.replace('CLASS D', "")
            actual_name = actual_name.replace('CLASSE', "")
            actual_name = actual_name.replace('CLASEXP', "")
            actual_name = actual_name.replace('EXP', "")
            actual_name = actual_name.replace('CLASS', "")
            actual_name = actual_name.replace('ISS', "")
            actual_name = actual_name.replace('SExr', "")
            actual_name = actual_name.replace('EXL', "GU")
            actual_name = actual_name.replace('Payroll', "")
            actual_name = actual_name.replace('Attn', "")
            actual_name = actual_name.replace('GEXP', "")
            print("full_name",actual_name)
            return actual_name
        except Exception as e:
            full_name = 'null'
            return full_name
    def get_paystub_date(self,text):
        try:
            val = re.findall(
                r'(\w*[A-Za-z]\d{1}\d{2}[./-](19|20|21|22|23|24)\d\d)|(\w*[A-Za-z]\d{1}[./-]\d{2}[./-](19|20|21|22|23|24)\d\d)'
                r'|(\d{2}\s?[./-]\d{2}[./-](19|20|21|22|23|24)\d\d)|(\d{2}\s\d{2}\s(19|20|21|22|23|24)\d\d)'
                r'|(\d{2}[./-]\d{2}\s?(19|20|21|22|23|24)\d\d)|(\d{1,2}\s?[./-]\d{2}[./-]\s?\d{2}\s?\d{2})'
                r'|(\d{2}\d{2}[./-](19|20|21|22|23|24)\d\d)|(\d{2}[./-]\d{2}\s[./-](19|20|21|22|23|24)\d\d)'
                r'|(([0-9]|0[0-9]|1[0-9])[./-]([0-9][0-9]|[0-9])[./-]\d\d)|(([0-9]'
                r'|0[0-9]|1[0-9])[./-]([0-9][0-9]|[0-9])[./-](19|20|21|22|23|24)\d\d|(\d{2}\d{2}[./-]\d\d))\b', text)

            for item in val:
                self.date_val1.append(" ".join(item))
            ##print("Date", date_val1)
            string_date = " ".join(map(str, self.date_val1))
            self.date_val = re.findall(r'\d{2}\s?[./-]?\d{2}\s?[./-]?\d{2,4}', string_date)
            ##print("Date1", date_val)
            for dob in self.date_val:
                if 'o' in dob:
                    dob = dob.replace("o", "0")
                if ' ' in dob:
                    dob = dob.replace(" ", "")
                if "/" in dob:
                    dob = dob.replace(" ", "")
                    dob = dob.replace("/", "")
                if "-" in dob:
                    dob = dob.replace(" ", "")
                    dob = dob.replace("-", "")
                if "." in dob:
                    dob = dob.replace(" ", "")
                    dob = dob.replace(".", "")

                dob = dob[0:2] + '/' + dob[2:4] + '/' + dob[4:8]
                self.date.append(dob)
            for value in self.date[:2]:

                if re.match(r'\b\d{2}[./-]\d{2}[./-]\d{2}\b', value):
                    self.actual_date.append(datetime.datetime.strptime(value, '%m/%d/%y').strftime('%y/%m/%d'))
                else:
                    self.actual_date.append(datetime.datetime.strptime(value, '%m/%d/%Y').strftime('%Y/%m/%d'))
            data = " ".join(map(str, self.actual_date))
            if re.match(r'\b\d{2}[./-]\d{2}[./-self.]\d{2}\b', data):
                ending_date = max(self.actual_date)
                starting_date = min(self.actual_date)
                if ending_date != "" and starting_date != "":
                    ending_date = datetime.datetime.strptime(ending_date, '%y/%m/%d').strftime('%m/%d/%y')
                    starting_date = datetime.datetime.strptime(starting_date, '%y/%m/%d').strftime('%m/%d/%y')
                    self.employment_Start_date = dt.strptime(ending_date, "%m/%d/%Y")
                    self.pay_date = dt.strptime(starting_date, "%m/%d/%Y")
            else:
                ending_date = max(self.actual_date)
                starting_date = min(self.actual_date)
                if ending_date != None and starting_date != None:
                    ending_date = datetime.datetime.strptime(ending_date, '%Y/%m/%d').strftime('%m/%d/%Y')
                    starting_date = datetime.datetime.strptime(starting_date, '%Y/%m/%d').strftime('%m/%d/%Y')
                    self.employment_Start_date = dt.strptime(ending_date, "%m/%d/%Y")
                    self.pay_date = dt.strptime(starting_date, "%m/%d/%Y")
            frequency = abs((self.pay_date - self.employment_Start_date).days)
            if frequency == 14 or frequency == 13:
                self.pay_frequency = 'Bi-Weekly'
            elif frequency == 7 or frequency == 6:
                self.pay_frequency = 'Weekly'
            elif frequency == 30 or frequency == 31:
                self.pay_frequency = 'Monthly'
            start_date=self.employment_Start_date.date()
            print(start_date)
            print("pay_frequency",self.pay_frequency)
            return str(start_date), self.pay_frequency
        except Exception as E:
            print(E)
            start_date, self.pay_frequency = "null", "null"
            return start_date, self.pay_frequency
    def gross_net(self,text):
        try:
            value = re.findall(
                r'((=?Gross Pay|Brose Pay|Amount|Gross Earnings|Net Pay)|\s?\$?\d{1,3}\s?\,?\s?\d+\.?\d+?)\b', text)
            for item in value:
                self.data.append("".join(item))
            string_date = " ".join(map(str,self.data))

            if re.search('(\w+\s\w+\s?\s?\$\d{1,3}\s?\,?\s?\d+\.?(\d+)?)', string_date) is not None:
                get_value = re.findall(
                    r'(=?(Gross Pay|Brose Pay|Amount|Gross Earnings|Net Pay)|\s?\s?\$\d{1,3}\s?\,?\s?\d+\.?\d+?)\b',
                    string_date)
            else:
                get_value = re.findall(
                    r'(=?(Gross Pay|Brose Pay|Amount|Gross Earnings|Net Pay)\s?\s?\d{1,3}\s?\,?\s?\d+\.?\d+?)\b',
                    string_date)

            for item in get_value:
                self.data1.append("".join(item))
            get_gn_value = "".join(map(str, self.data1))
            gross_net_value = re.findall(
                r'((=?Gross Pay|Brose Pay|Amount|Gross Earnings|Net Pay)\s?\s?\$?\d{1,3}\s?\,?\s?\d+\.?(\d+)?)',
                get_gn_value)
            for item in gross_net_value:
                self.value2.append("".join(item))
            string_date1 = " ".join(map(str, self.value2))

            gross_net_value = re.findall(r'(\s?\$?\d{1,3}\s?\,?\s?\d+\.?(\d+)?)', string_date1)
            print(gross_net_value)
            if re.search(r'\$?\d{2,3}\.\d+',gross_net_value[1][0].replace(" ", "")):
                    return gross_net_value[0][0].replace(" ", ""), gross_net_value[1][0].replace(" ", "")
            else:
                return gross_net_value[0][0].replace(" ", ""), gross_net_value[2][0].replace(" ", "")
        except Exception as e:
            print(e)
    def get_details(self,text):
        street, state, zipcode, city=self.get_paystub_Address(text)
        full_name=self.get_paystub_name(text,street)
        starting_date,pay_freq=self.get_paystub_date(text)
        gross_pay,net_pay=self.gross_net(text)
        return state,city,full_name,starting_date,pay_freq,gross_pay,net_pay
