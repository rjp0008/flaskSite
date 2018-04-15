import csv
import math
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

    def total(self):
        running_total = 0
        for item in self.data:
            if 'Hide from Budgets & Trends' not in item[2]:
               running_total += float(int(math.ceil(float(item[1]))) - float(item[1]))
        return running_total

ru = RoundUp()
ru.read_file(r'C:\Users\rjp00\Downloads\transactions.csv')
print(ru.total())