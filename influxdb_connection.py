import os
import sys
from influxdb import InfluxDBClient
import csv
from datetime import date

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
	def __init__(self, DEFAULTPATH = './output/', CSV_SEPARATOR = ',', INCIDENTE = 'incidenti', TEMPISTICHE = 'tempistiche', DATI_PER_ORA = 'dati_per_ora'):
		self.DEFAULTPATH = DEFAULTPATH
		self.CSV_SEPARATOR = CSV_SEPARATOR
		self.INCIDENTE = INCIDENTE
		self.TEMPISTICHE = TEMPISTICHE
		self.DATI_PER_ORA = DATI_PER_ORA

	#creates or locates path
	def createPath(self):
		if os.path.exists(self.DEFAULTPATH) == False:
			os.makedirs(self.DEFAULTPATH)
			print('Created Directory!')
		if not os.path.exists(self.DEFAULTPATH) == False:
			print('Directory is already there!')

	#cycles at the input datatype and then if
	def writeCSV(self, dataList):
		dataLength = len(dataList)
		with open(self.DEFAULTPATH +'data.csv', 'w', newline='') as csvfile:
			file = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			print('creacsv')
			for i in range(dataLength):
				if(dataList[i] == self.INCIDENTE):
					print('incidente')
					file.writerow("data" + self.CSV_SEPARATOR + self.INCIDENTE + self.CSV_SEPARATOR)
				if(dataList[i] == self.TEMPISTICHE):
					print('tempistiche')
					file.writerow("data" +  self.CSV_SEPARATOR + self.TEMPISTICHE + self.CSV_SEPARATOR)
				if(dataList[i] == self.DATI_PER_ORA):
					print('datiora')
					file.writerow("data" +  self.CSV_SEPARATOR + self.DATI_PER_ORA + self.CSV_SEPARATOR)