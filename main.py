import requests, logging, pyodbc, yaml, os, json

#region Global variables
config = yaml.safe_load(open("config.yml"))

COMPANY = config["COMPANY"]
API_URL = config["API_URL"]
PRIORITY_API_USERNAME= config["PRI_API_USERNAME"]
PRIORITY_API_PASSWORD= config["PRI_API_PASSWORD"]
#endregion

#region setup Error Logging
path = r"error.log"
assert os.path.isfile(path)
logging.basicConfig(filename=path, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Logging started.')
#endregion

#region Data Logging
def send_email(subject, body):
    server = smtplib.SMTP("smtp.gmail.com")
    MSG = f"Subject: {subject}\n\n {body}"
    server.sendmail(my_email, RECEIVER_EMAIL, MSG)

    server.quit()

def log_response(res):
    if res.ok:
        logging.info("Data posted succesfully to Priority.")
    elif res.status_code == 409:
        # send_email(f"Error message: {res.json()['error']['message']}")
        logging.error(f"Error message: {res.json()['error']['message']}")
        # send_email("Error", f"Error message: {res.json()['error']['message']}")
    elif res.status_code == 500:
        logging.error("Status code 500: Either Priority or the Flask server is down/having problems.")
        # send_email("Error", "Status code 500: Either Priority or the Flask server is down/having problems.")
    else:
        logging.error(f"Error status code: {res.status_code}")
        # send_email("Error", f"Error status code: {res.status_code}")
#endregion

#region Connect to DB
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=RM-SQL01\SIGMANEST;'
                      'Database=SNDBase;'
                      'UID=SNUser;'
                      'PWD=BestNest1445')

cursor = conn.cursor()
inner_conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=RM-SQL01\SIGMANEST;'
                      'Database=SNDBase;'
                      'UID=SNUser;'
                      'PWD=BestNest1445')
cursor1 = inner_conn.cursor()
#endregion

#region Priority patch example
def update_cost(PARTNAME, PRICE):
    r = requests.patch(f"{API_URL}{COMPANY}/LOGPART('{partname}')", json={ 'PRICE': float(price) }, auth=(PRIORITY_API_USERNAME, PRIORITY_API_PASSWORD))
    log_response(r)
    print (r)
    if (r.status_code == 200):
        is_passed = True
    else:
        is_passed = False
    return (is_passed)
#endregion


#region Sigma update
def update_records (ID):
    sql1 = '''UPDATE [SNDBase].[dbo].[PRICE_CHANGES] SET IS_UPDATED = 1 WHERE ID = {}'''.format(ID)
    cursor1.execute(sql1)
    # conn.commit()    
    return ()
#endregion

#region PYODBC 
sql = '''SELECT ID, PARTCODE, UNIT_COST FROM [SNDBase].[dbo].[PRICE_CHANGES] WHERE IS_UPDATED = 0 ORDER BY ID ASC'''
cursor.execute(sql)
for r in cursor:
    partname = r.PARTCODE
    price = r.UNIT_COST
    update_cost(partname, price)
    update_records (r.ID)

cursor1.close()
cursor.close()
conn.commit()
inner_conn.commit()
inner_conn.close()
conn.close()


#endregion