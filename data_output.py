#import os
import sys
#const
# FILE = 0
# DB = 1
DEFAULTPATH = './output/'
CSV_SEPARATOR = ','
#IP_ADDRESS = 'localhost'
#DBNAME = 'simulatore_incidenti'
INCIDENTE = 'incidenti'
TEMPISTICHE = 'tempistiche'
DATI_PER_ORA = 'dati_per_ora'
# USER = 'user'
# PASSWORD = 'password'

def printTxt():
	orig_stdout = sys.stdout

	f = open('./output.txt', 'w')
	sys.stdout = f

	for i in range(2):
		print('i = ', i)

	sys.stdout = orig_stdout
	f.close()