import paramiko
import os
import re
import pymysql
from datetime import datetime, timedelta, timezone



def connect_to_sftp(host, port, username, key_path=None):
    try:
        transport = paramiko.Transport((host, port))
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
        transport.connect(username=username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Successfully connected to SFTP server")
        return sftp, transport
    except Exception as e:
        print(f"Failed to connect to SFTP: {e}")
        raise


def read_logs(sftp, remote_path):
    try:
        file = sftp.open(remote_path, 'r')
        if not file:
            print(f"No files found in: {remote_path}")
            return
        logs = file.read().decode('utf-8')
        log_lines = logs.split('\n')
        return log_lines
    except Exception as e:
        print(f"Error reading logs: {e}")
        raise

def connect_to_mariadb():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as err:
        print(f"Error connecting to MariaDB: {err}")
        raise


def create_log_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sftp_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            log_date DATE NOT NULL,
            log_time TIME NOT NULL,
            ip_address VARCHAR(45),
            source_host VARCHAR(255),
            UNIQUE KEY uniq_log_datetime (log_date, log_time)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            log_date DATE NOT NULL,
            log_time TIME NOT NULL,
            log_message TEXT NOT NULL,
            UNIQUE KEY uniq_log_entry (log_date, log_time)
        )
    """)
def insert_log(cursor, log_date, log_time, ip_address, source_host, table):
    if not re.match(r'^\w+$', table):
        raise ValueError(f"Invalid table name: {table}")
    cursor.execute(f"""
        INSERT IGNORE INTO {table} (log_date, log_time, ip_address, source_host)
        VALUES (%s, %s, %s, %s)
    """, (log_date, log_time, ip_address, source_host))
def insert_raw_logs(cursor, log_date, log_time, message, table):
    if not re.match(r'^\w+$', table):
        raise ValueError(f"Invalid table name: {table}")
    cursor.execute(f"""
        INSERT IGNORE INTO {table} (log_date, log_time, log_message)
        VALUES (%s, %s, %s)
    """, (log_date, log_time, message))
def get_logs_from_db(cursor):
    try:
        cursor.execute("SELECT * FROM sftp_logs ORDER BY log_date ASC, log_time ASC")
        results = cursor.fetchall() 
        return results
    except pymysql.MySQLError as err:
        print(f"Error fetching logs: {err}")
        return [123]
    
def get_raw_logs_from_db(cursor, table, start_datetime, end_datetime):
    if not re.match(r'^\w+$', table):
        raise ValueError(f"Invalid table name: {table}")

    try:
        query = f"""
            SELECT * FROM {table}
            WHERE CONCAT(log_date, ' ', log_time) BETWEEN %s AND %s
            ORDER BY log_date ASC, log_time ASC
        """
        cursor.execute(query, (start_datetime, end_datetime))
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Error fetching logs: {err}")
        return [321]

def parse_log_line(log_line):
    try:
        match = re.search(r'^(\w{3}\s+\d{1,2}) (\d{2}:\d{2}:\d{2}).*?from (\d+\.\d+\.\d+\.\d+)', log_line)
        if match:
            raw_date = match.group(1)
            raw_time = match.group(2)
            ip_address = match.group(3)
            parsed_date = datetime.strptime(f"{datetime.now().year} {raw_date}", "%Y %b %d").date()
            parsed_datetime = datetime.strptime(raw_time, "%H:%M:%S")
            parsed_time = parsed_datetime.time()

            return parsed_date, parsed_time, ip_address
        else:
            print(f"Could not parse line: {log_line}")
            return None, None, None
    except Exception as e:
        print(f"Error parsing log line: {e}")
        return None, None, None
    
def parse_raw_log_line(log_line):
    try:
        # Match: 'May 22 18:14:47' and capture the rest of the line
        match = re.match(r'^(\w{3}\s+\d{1,2}) (\d{2}:\d{2}:\d{2}) (.*)$', log_line)
        if match:
            raw_date = match.group(1)
            raw_time = match.group(2)  
            message = match.group(3)   

            parsed_date = datetime.strptime(f"{datetime.now().year} {raw_date}", "%Y %b %d").date()
            parsed_time = datetime.strptime(raw_time, "%H:%M:%S").time()

            return parsed_date, parsed_time, message
        else:
            print(f"Could not parse line: {log_line}")
            return None, None, None
    except Exception as e:
        print(f"Error parsing log line: {e}")
        return None, None, None