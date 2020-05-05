from influxdb import InfluxDBClient
from influxdb import DataFrameClient
import os

#const
FILE = 0
DB = 1
DEFAULTPATH = './output/'
CSV_SEPARATOR = ','
#IP_ADDRESS = 'localhost'
IP_ADDRESS = 'localhost'
DBNAME = 'simulatore_incidenti'
INCIDENTE = 'incidenti'
TEMPISTICHE = 'tempistiche'
DATI_PER_ORA = 'dati_per_ora'
USER = 'user'
PASSWORD = 'password'

Tdata.append()

HOST_ = 'localhost'
PORT_ = 8086

#Influx
class DBConnect:
	def __init__(self, host = HOST_, port = PORT_, dbname = DBNAME):
        self.client = InfluxDBClient(host = host, port = port)
        self.dbname = dbname
		self.flagConnection = 0

	#method used to check if there is connection to the Database Instance
    def checkConnection(self):
        client.ping()
		flagConnection = 1
    

	#method used to Select the preferred Database
    def dbSelect(self):
		if(flagConnection == 1):
			client.switch_database(dbname)
			if(dbname == None):
				client.create_database(dbname)
				client.switch_database(dbname)
		else:
            checkConnection()
			if(flagConnection == 0):
				print('Cannot connect to Database')
	
	#method used to write the json output into the database
	def dbWrite(self, json_data):
		client.write_points(json_data)

	#method used to close the connection with the Database
	def dbDisconnect(self):
		client.close()

class FileOutput:
	def __init__(self, path, separator = CSV_SEPARATOR):
		self.path = path
		self.separator = separator
		
	def writeCSV(self, tipoDato, dato):
		output_path = open(self.path + tipoDato + '.csv', "r+")
		isFile = os.output_path.isfile(path)
		if(isFile != True):
			output_path.writelines(L) for L = [tipoDato + separator])
			if(tipoDato == INCIDENTE):
				output_path.write(separator)
				output_path.writelines(L) for L = [tipoDato + "." + "" ]
			if(tipoDato == TEMPISTICHE):
				output_path.write(separator)
				output_path.writelines(L) for L = [tipoDato + "." + "" ]
			if(tipoDato == DATI_PER_ORA):
				output_path.write(separator)
				output_path.writelines(L) for L = [tipoDato + "." + "" ]
