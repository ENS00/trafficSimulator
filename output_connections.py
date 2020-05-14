import os
from influxdb import InfluxDBClient
import csv

class DBOutput():
	def __init__(self, host = 'localhost', dbname = 'simulatore_incidenti', port = 8086):
		self.host = host
		self.port = port
		self.dbname = dbname
		self.client = InfluxDBClient(host = self.host, port = self.port)
		self.flagConnection = 0

	# method used to check if there is connection to the Database Instance
	def dbCheckConn(self):
		self.client.ping()
		self.flagConnection = 1
		print(self.client.get_list_database())
		print("It is possible to connect to the InfluxDB instance!!")

	# method used to Select the preferred Database
	def chooseDB(self):
		if(self.flagConnection == 1):
			self.client.create_database(self.dbname)
			self.client.switch_database(self.dbname)
		else:
			self.dbCheckConn()
			if(self.flagConnection == 0):
				print('Cannot connect to Database!!!')

	# method used to write the json output into the database
	def writeOutput(self, data):
		self.client.write_points([data])

	# method used to close the connection with the Database
	def closeConnection(self):
		self.client.close()

class CSVOutput():
	def __init__(self, PATH = './output/'):
		self.PATH = PATH

	#cycles at the input datatype and then if
	def writeCSV(self, data):
		#copies data into a variable and then deletes the whole file
		datatype = data['measurement']
		data.update(data['tags'])
		del data['tags']
		data.update(data['fields'])
		del data['fields']
		del data['measurement']

		#checks if the directory exists, if False then it creates the directory
		if os.path.exists(self.PATH) == False:
			os.makedirs(self.PATH)
			#print('Created Directory!')
			with open(self.PATH + datatype + '.csv', 'w', newline='') as csvfile:
				file = csv.DictWriter(csvfile, data.keys())
				file.writeheader()

		#if True then it just appends the data
		if not os.path.exists(self.PATH) == False:
			#print('Directory is already there, appending just data!')
			with open(self.PATH + datatype + '.csv', 'a', newline='') as csvfile:
				file = csv.DictWriter(csvfile, data.keys())
				file.writerow(data)
				