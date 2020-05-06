from influxdb import InfluxDBClient

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