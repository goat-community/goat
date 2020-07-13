import boto3
import yaml 
import sys 
import os.path
from os import path

def load_spaces_yaml():
    if path.exists("/opt/config/db/spaces.yaml") == True:
        #Load key_id and secret_access_key from spaces.yaml
        with open("/opt/config/db/spaces.yaml", 'r') as stream:
            conf = yaml.load(stream, Loader=yaml.FullLoader)

        key_id = conf["key_id"]
        secret_access_key = conf["secret_access_key"]
        return key_id,secret_access_key
    else:
        print('You have no spaces.yaml file in your config folder. You need the credentials in this file to interact with DigitalOcean Spaces.')
        sys.exit()
    

def space_connect(region_name):
    
    key_id = load_spaces_yaml()[0]
    secret_access_key = load_spaces_yaml()[1]

    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=str(region_name),
                            endpoint_url='https://' + str(region_name) + '.digitaloceanspaces.com',
                            aws_access_key_id=key_id,
                            aws_secret_access_key=secret_access_key)
    return client

def list_spaces():
    regions = ['ams3', 'fra1']
    #array0 - ams3
    #array1 - nyc3
    #array2 - sgp1
    #array3 - sfo2
    available_spaces = [[], [], [], []]
    b = -1
    if b < 5:
        for i in regions:
            b += 1
            # print("checking servers in " + i)
            response = space_connect(i).list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            for space_num in buckets:
                # print(space_num)
                available_spaces[b].append(str(space_num))

    return available_spaces

def list_files(space_name,region_name, dir):
    #take argument for particular directory file listing
    #Put a try:
    r = space_connect(region_name).list_objects(Bucket=space_name, Prefix=dir)
    files = r.get('Contents')
    i = 0
    p = str(files)
    fnames = []

    if p == "None":
        print("No Data available")
    else:
        for file in files:
            if len(file) > 0:
                i += 1
            else:
                continue
            file_detect = file['Key']
            if file_detect[-1:] == '/':
                file_type = "Folder"
            else:
                file_type = "File"

            print("Object: ")
            print("     Name: " + file['Key'] + " [" + file_type + "]")
            print("     Size: " + str(file['Size']) + " bytes")
            date, time = str(file['LastModified']).split(" ")
            print("     Last Modified: ")
            print("             Date: " + date)
            # later make function that determines from 2018-09-29 09:00:17.235000+00:00
            # to detect date, time, and timezone - GMT, etc.
            # time, date - done already
            timeh, useless = time.split(".")
            print("             Time: " + timeh)
            fnames.append(file['Key'])
        return fnames

def upload_file(space_name, region_name, local_file, upload_name):
    s3 = space_connect(region_name)
    try:
        s3.upload_file(local_file, space_name, upload_name)
        message = "Success"
        return message
        # pass
    except Exception as e:
        message = "Error occured. Check Space name, etc"

    return message
    #upload_file('my-space-name', 'sfo2', 'test.txt', 'me1.txt')


def download_file(space_name, region_name, file_name, local_path):
    s3 = space_connect(region_name)
    try:
        s3.download_file(space_name, file_name, local_path)
        print("Data written to ->" + local_path)
    except:
        print("Error: Maybe file does not exist, or check the path you are saving to ")
        print("Usage: download file_to_download_from_the_space file_name_to_save_on_disk")
        print("Ex: download mytest-from-cloud docs.txt")
    #USAGE: download_file('space_name', 'nyc3', 'file_in_space.txt', 'file.txt')

#upload_file('goat','fra1','setup_db.py','setup_db.py')

def download_raw_data(space_name, region_name, dir):
    fnames = list_files(space_name,region_name, dir)
    for i in fnames[1:]:
        download_file(space_name,region_name, i , '/opt/data/'+i.split('/')[-1])

#download_raw_data('goat', 'fra1','raw_data/'+'ffb')
