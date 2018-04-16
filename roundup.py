import csv
import math
import datetime

class RoundUp():
    def __init__(self):
        self.data = []

    def read_file(self,path):
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader.fieldnames)
            for row in reader:
                self.data.append([row['Date'], row['Amount'],row['Category']])

    def print(self):
        for item in self.data:
            print(item)

    def total_to_console(self):
        running_total = 0
        curr_month = datetime.datetime.now().month
        for item in self.data:
            if 'Hide from Budgets & Trends' not in item[2]:
               running_total += float(int(math.ceil(float(item[1]))) - float(item[1]))
            if curr_month != datetime.datetime.strptime(item[0],'%m/%d/%Y').month:
                date = datetime.datetime.strptime(item[0], '%m/%d/%Y')
                print("{0}/{1}-{2}".format(date.month,date.year,math.ceil(running_total)))
                curr_month = datetime.datetime.strptime(item[0],'%m/%d/%Y').month
                running_total = 0


ru = RoundUp()
ru.read_file(r'C:\Users\rjp00\Downloads\transactions (2).csv')
ru.total_to_console()