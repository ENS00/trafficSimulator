import os
from influxdb import InfluxDBClient
import csv

class Output():
	def writeData(self, data):
		pass

	def closeConnection(self):
		pass

class DBOutput(Output):
	def __init__(self, host = 'localhost', dbname = '', port = 8086):
		self.host = host
		self.port = port
		self.dbname = dbname
		self.client = InfluxDBClient(host = self.host, port = self.port)
		self.flagConnection = 0
		self.chooseDB()

	# method used to check if there is connection to the Database Instance
	def dbCheckConn(self):
		try:
			self.client.ping()
		except Exception as e:
			print('W: Cannot reach database "%s@%s:%i' % (self.dbname, self.host, self.port))
			print('E: Details:',e)
			self.flagConnection = 0
		else:
			self.flagConnection = 1

	# method used to Select the preferred Database
	def chooseDB(self):
		if(self.flagConnection == 1):
			self.client.create_database(self.dbname)
			self.client.switch_database(self.dbname)
		else:
			self.dbCheckConn()
			if(self.flagConnection == 1):
				self.client.create_database(self.dbname)
				self.client.switch_database(self.dbname)

	# method used to write the json output into the database
	def writeData(self, data):
		self.client.write_points([data])

	# method used to close the connection with the Database
	def closeConnection(self):
		self.client.close()
		print('I: Connection closed')

class CSVOutput(Output):
	def __init__(self, PATH = './output/'):
		self.PATH = PATH
		self.flagConnection = 1
		# checks if the directory exists, if False then it creates the directory
		if os.path.exists(self.PATH) == False:
			try:
				os.makedirs(self.PATH)
			except PermissionError as e:
				self.flagConnection = 0
				print('W: Could not create directory "%s"'%self.PATH)
				print('W: You need to change permissions and reload the simulation to save new data')
				print('E: Details: ',e)
			else:
				print('I: Created new directory "%s"'%self.PATH)

	# cycles at the input datatype and then if
	def writeData(self, data):
		if self.flagConnection:
			# manipulates a copy and not the original object
			data = dict(data)
			# copies data into a variable and then deletes the unnecessary parameters
			datatype = data['measurement']
			data.update(data['tags'])
			del data['tags']
			data.update(data['fields'])
			del data['fields']
			del data['measurement']
			completepath = self.PATH + datatype + '.csv'

			if os.path.exists(completepath) == False:
				# create new file and write header + data
				try:
					with open(completepath, 'w', newline='') as csvfile:
						file = csv.DictWriter(csvfile, data.keys())
						file.writeheader()
						file.writerow(data)
						print('I: Created new file "%s"'%completepath)
				except PermissionError as e:
					print('W: I need rw permissions to write in "%s", make sure the folder has the right file system permissions'%self.PATH)
					print('W: You need to change permissions and reload the simulation to save new data')
					print('E: Details: ',e)
					self.flagConnection = 0
			else:
				# appends the data
				with open(completepath, 'a', newline='') as csvfile:
					file = csv.DictWriter(csvfile, data.keys())
					file.writerow(data)
