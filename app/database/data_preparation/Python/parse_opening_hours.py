import json, collections
import psycopg2
import re
import calendar
import yaml

with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)

secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]

daynames = ["Mo","Tu","We","Th","Fr","Sa","Su","PH"]
timepattern = re.compile("[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]")
day_numeration = dict({"Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7})

con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
    db_name, user, port, host, password))

cursor = con.cursor()




#pattern2 = r'([A-z]{2}-?[A-z]{2}?)[ ]?([0-2][0-9]:[0-5][0-9]-?[0-2][0-9]:[0-5][0-9]?)'

def parse_opening_time():
    cursor.execute('''select osm_id, opening_hours from pois where (new_opening_hours = 'null' and amenity='fuel')''')
    #cursor.execute('''select osm_id, opening_hours from pois where new_opening_hours = 'null' ''')
    opening_times = cursor.fetchall()

    for opening_time in opening_times: 
        osm_id = opening_time[0]
        new_format = parse_to_new_format(opening_time[1])
        print('###', osm_id, type(new_format))

        update_query = str('UPDATE pois set new_opening_hours =\'' + new_format +'\'::jsonb where osm_id = ' + str(osm_id))
        update_query = '''UPDATE pois set new_opening_hours =\'%s\'::jsonb where osm_id = %s''' % (new_format,osm_id)
        print('###---', update_query)
        cursor.execute('''UPDATE pois set new_opening_hours =\'%s\'::jsonb where osm_id = %s''' % (new_format,osm_id))
        con.commit()
        #break
    
def check_if_day(iday):
    passed = False
    for cvalue in daynames:
        if iday == cvalue:
            passed = True
            break
    return passed

def parse_to_new_format(time):
    ojson_format = collections.OrderedDict([
        ("Mo", list()),
        ("Tu", list()),
        ("We", list()),
        ("Th", list()),
        ("Fr", list()),
        ("Sa", list()),
        ("Su", list())
    ])
    bufferofdays = list()
    bufferoftimes = list()
    buffercurrentday = ""
    buffercurrenttime = ""
    searchstate = 0
    #0 - initial
    #5 - day pending
    #10 - found a day
    #13 - found a dash
    #15 - day pending after a dash
    #20 - found a second day in a range
    #25 - found a number
    #30 - number checked
    for c in time:
        if searchstate == 0:
            if c.isalpha():
                buffercurrentday += c
                searchstate = 5
        elif searchstate == 5:
            if c.isalpha():
                buffercurrentday += c
                if check_if_day(buffercurrentday):
                    bufferofdays.append(buffercurrentday)
                    buffercurrentday = ""
                    searchstate = 10
                else:
                    buffercurrentday = ""
                    bufferofdays = list()
                    searchstate = 0
            else:
                buffercurrentday = ""
                bufferofdays = list()
                searchstate = 0
        elif searchstate == 10:
            if c.isalpha():
                buffercurrentday += c
                searchstate = 5
            elif c == "-":
                searchstate = 13
            elif c.isdigit():
                buffercurrenttime += c
                searchstate = 25
            elif c != " " and c != "," and c != ";":
                bufferofdays = list()
                searchstate = 0
        elif searchstate == 13:
            if c.isalpha():
                buffercurrentday += c
                searchstate = 15
            else:
                buffercurrentday = ""
                bufferofdays = list()
                searchstate = 0
        elif searchstate == 15:
            if c.isalpha():
                buffercurrentday += c
                if check_if_day(buffercurrentday):
                    startingday = bufferofdays[len(bufferofdays)-1]
                    sdn = day_numeration[startingday]
                    fdn = day_numeration[buffercurrentday]
                    adder = 0
                    if sdn > fdn:
                        adder = 7
                    for key, value in ojson_format.items():
                        if day_numeration[key]+adder >= sdn and (day_numeration[key] <= fdn+adder):
                            if key != startingday:
                                bufferofdays.append(key)
                    buffercurrentday = ""
                    searchstate = 20
                else:
                    buffercurrentday = ""
                    searchstate = 0
            else:
                buffercurrentday = ""
                searchstate = 0
        elif searchstate == 20:
            if c.isalpha():
                buffercurrentday += c
                searchstate = 5
            elif c.isdigit():
                buffercurrenttime += c
                searchstate = 25
            elif c != " " and c != "," and c != ";":
                bufferofdays = list()
                searchstate = 0             
        elif searchstate == 25:
            if c.isdigit() or c == "-" or c == ":" or c == " ":
                if len(buffercurrenttime)<11:
                    buffercurrenttime += c
                    if len(buffercurrenttime) == 11:
                        if timepattern.match(buffercurrenttime):
                            bufferoftimes.append(buffercurrenttime)
                            buffercurrenttime = ""
                            searchstate = 30
            else:
                buffercurrenttime = ""
                bufferofdays = list()
                bufferoftimes = list()
                searchstate = 0
        elif searchstate == 30:
            print (bufferofdays)
            print (bufferoftimes)
            if c.isalpha():
                for key, value in ojson_format.items():
                    for dvalue in bufferofdays:
                        if key == dvalue:
                        
                            for tvalue in bufferoftimes:
                                value.append(tvalue)
                    ojson_format[key] = value
                bufferofdays = list()
                bufferoftimes = list()
                buffercurrentday += c
                searchstate = 5
            elif c.isdigit():
                buffercurrenttime += c
                searchstate = 25
            elif c != " " and c != "," and c != ";":
                for key, value in ojson_format.items():
                    for dvalue in bufferofdays:
                        if key == dvalue:
                            
                            for tvalue in bufferoftimes:
                                value.append(tvalue)
                    ojson_format[key] = value
                bufferofdays = list()
                bufferoftimes = list()
                searchstate = 0
    if searchstate == 30:
        for key, value in ojson_format.items():
            for dvalue in bufferofdays:
                if key == dvalue:
                    
                    for tvalue in bufferoftimes:
                        value.append(tvalue)
                    ojson_format[key] = value
    passage = False
    for key, value in ojson_format.items():
        if len(value) > 0:
            passage = True
            break
    if passage:
        for key, value in ojson_format.items():
            if len(value) == 0:
                value.append("closed")
                ojson_format[key] = value
        return json.dumps(ojson_format)
    else:
        return json.dumps(None)

parse_opening_time()

con.commit()