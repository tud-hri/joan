import threading
import io
import csv

from time import sleep
#from datetime import datetime


class DataWriter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.filehandle = None
        self.writer = None
        self.fieldnames = []

    def run(self):
        print(self.is_alive())
        #self.fake()

    def columnnames(self, keys=[]):
        # filters keys you want from the data and put them as header in the csv file
        self.fieldnames = keys

    def open(self, filename, buffersize=io.DEFAULT_BUFFER_SIZE):
        print('buffersize', buffersize)
        self.filehandle = open(filename, 'w', buffering=buffersize)
        self.writer = csv.DictWriter(self.filehandle, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def close(self):
        self.filehandle.close()

    def write(self, data={}):
        row = {}
        row['time'] = 'fixed' #datetime.now()
        row.update(data)
        self.writer.writerow(row)
'''
    def fake(self):

        dRows = []
        for huge in range(0, 10000):
            dRows.append({'first_name': 'Baked', 'last_name': 'Beans'})
            dRows.append({'first_name': 'Lovely', 'last_name': 'Looks'})
            dRows.append({'first_name': 'Wonderful', 'last_name': 'World'})
            dRows.append({'first_name': 'Amazing', 'last_name': 'Ananas'})
            dRows.append({'first_name': 'Great', 'last_name': 'Goods'})

        #print(datetime.now())
        for row in dRows:
            self.write(data=row)
        self.close()  # close thread
        #print(datetime.now())

#buffer=2
#2020-03-24 14:09:57.126389,Baked,Beans
#2020-03-24 14:09:57.351302,Great,Goods
#225

#buffer = io.DEFAULT_BUFFER_SIZE = 8192
#649795
#429372
#220

#buffer = 512kb = 524288 bytes
# 890516
# 658409
# 242

#met while thread.is_alive()
#        pass
#    thread.close()

#21.306476
#20.858028
# 448

#buffer = 1  # na elke newline
#23.200983
#22.715844
# 485

# Daemon aan of uit maak niets uit

#time fixed meegeven i.p.v. datetime.now() aanroepen
#934717
#812659
# 112
# dit gaat dus het snelst

if __name__ == "__main__":
    filename = "test.csv"
    fieldnames = ['first_name', 'last_name']
    fieldnames.insert(0, 'time')

    thread = DataWriter()
    #thread.setDaemon(True)
    thread.columnnames(fieldnames)
    thread.open(filename=filename, buffersize=io.DEFAULT_BUFFER_SIZE)
    thread.start()

    for test in range(0, 10):
        print(test)
        sleep(1)

'''
