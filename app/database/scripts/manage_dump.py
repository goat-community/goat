import os 
from datetime import date 
import argparse
import sys
from argparse import RawTextHelpFormatter
from connect_to_spaces import *


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-d', help='Downloads a database dump from your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-u', help='Upload a database dump to your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-n', help='This is the namespace that will be used as folder name. e.g. -n muenchen')
parser.add_argument('-b', help='Backup your GOAT-Database before uploading.',action='store_true')

args = parser.parse_args()
namespace = args.n

if namespace is None:
    print('Error: Please select a namespace.')
    sys.exit()

today = str(date.today())

fname = namespace+'_dump'+today+'.sql'

def interaction(namespace,fname, args):

    if (args.b == True):
        print('Database dump will be generated and saved in /app/database/backups. Depending on the size this can take a while...')
        os.system('pg_dump -U postgres -d goat > /opt/backups/'+fname)

    if (args.u == True):
        print('File will be uploaded. Depending on the size this can take a while...')
        upload_file('goat','fra1','/opt/backups/'+fname,namespace+'/'+fname)

    if (args.d == True ):
        fnames = list_files('goat','fra1',namespace+'/')
        newest_file = sorted(fnames)[-1]
        download_file('goat', 'fra1', newest_file , '/opt/backups/'+newest_file.split('/')[1])

    if (args.b == False | args.u | False | args.d == False): 
        print('Error: Please select an argument that indicates your desired action.')


interaction(namespace,fname,args)

