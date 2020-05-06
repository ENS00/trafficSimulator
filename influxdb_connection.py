from influxdb import InfluxDBClient
from influxdb import DataFrameClient

#Influx methods
HOST_ = 'localhost'
PORT_ = 8086
CLIENT = InfluxDBClient(host = HOST_, port = PORT_)

#method used to check if there is connection to the Database Instance
def checkConnection():
	CLIENT.ping()
	flagConnection = 1
	print('client presente!')
    
#method used to Select the preferred Database
def dbSelect():
	if(flagConnection == 1):
		CLIENT.switch_database(dbname)
	if(dbname == None):
		CLIENT.create_database(dbname)
		CLIENT.switch_database(dbname)
	else:
		checkConnection()
	if(flagConnection == 0):
		print('Cannot connect to Database')
	
	#method used to write the json output into the database
def dbWrite(json_data):
	CLIENT.write_points(json_data)

#method used to close the connection with the Database
def dbDisconnect():
	CLIENT.close()

