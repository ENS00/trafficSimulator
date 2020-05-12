import os
import sys
from influxdb import InfluxDBClient
import csv

# Specchietti di visualizzazione casi limite

class DBOutput():
	def __init__(self):
		self.host = 'localhost'
		self.port = 8086
		self.dbname = 'simulatore_incidenti'
		self.client = InfluxDBClient(host = self.host, port = self.port)
		self.flagConnection = 0
		
	#method used to check if there is connection to the Database Instance
	def dbCheckConn(self):
		self.client.ping()
		self.flagConnection = 1
		print("E' possibile connettersi al db in pompa magna!!")
	
	#method used to Select the preferred Database
	def chooseDB(self):
		if(self.flagConnection == 1):
			self.client.switch_database(dbname)
		if(self.dbname == None):
			self.client.create_database(dbname)
			self.client.switch_database(dbname)
		else:
			dbCheckConn()
			if(flagConnection == 0):
				print('Cannot connect to Database!!!')
	
	#method used to write the json output into the database
	def writeOutput(self, data):
		self.client.write_points(data)
 
	#method used to close the connection with the Database
	def closeConnection(self):
		self.client.close()

class CSVoutput():
	def __init__(self):
		self.file
		self.DEFAULTPATH = './output/'
		self.CSV_SEPARATOR = ','
		self.INCIDENTE = 'incidenti'
		self.TEMPISTICHE = 'tempistiche'
		self.DATI_PER_ORA = 'dati_per_ora'

	def createPathAndSave(self):
		if not os.path.exists(self.DEFAULTPATH):
			os.makedirs(self.DEFAULTPATH)
		with open(os.path.join(self.DEFAULTPATH, self.file), 'wb') as temp_file:
			temp_file.write(buff)

	#cycles at the input datatype and then if
	def writeCSV(self, datatype):
		dataLength = len(datatype)
		with open('data.csv', 'w', newline='') as csvfile:
			self.file = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for i in range(dataLength):
				if(i == self.INCIDENTE):
					self.file.writerow()
				if(i == self.TEMPISTICHE):
					self.file.writerow()
				if(i == self.DATI_PER_ORA):
					self.file.writerow()
