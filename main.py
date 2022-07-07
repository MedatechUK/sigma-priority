import requests, logging, pyodbc, yaml, os

config = yaml.safe_load(open("config.yml"))

#region Global variables
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
    server = smtplib.SMTP(SMTP_URL)
    MSG = f"Subject: {subject}\n\n {body}"
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, MSG)

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
                      'Server=MEDA-LTP2620\PRI;'
                      'Database=demo;'
                      'UID=tabula;'
                      'PWD=12312312')

cursor = conn.cursor()
#endregion

#region PYODBC example
sql = '''INSERT INTO ZSFDC_LOADECO_M (LINE, BUBBLEID) 
            VALUES (?, ?)'''
val = (1, 2)
cursor.execute(sql, val)
conn.commit()
#endregion

#region Priority patch example
def update_cost(PARTNAME, PRICE):
    r = requests.patch(f"{API_URL}{COMPANY}/LOGPART('{PARTNAME}')", json={ 'PRICE': PRICE }, auth=(PRIORITY_API_USERNAME, PRIORITY_API_PASSWORD))
    log_response(r)
    return r.json()
#endregion
