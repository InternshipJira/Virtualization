from sftp_log_reader import connect_to_sftp, read_logs, parse_raw_log_line, connect_to_mariadb, insert_raw_logs
import os

sftp_config = {
    'host': os.getenv('SFTP_HOST'), 
    'port': int(os.getenv('SFTP_PORT', 22)),
    'username': os.getenv('SFTP_USERNAME'),
    'key_path': os.getenv('SFTP_KEY_PATH'),
    'remote_path': os.getenv('FILE_PATH')
}
db = connect_to_mariadb()
cursor = db.cursor()
try:
    
    for i in range(1,4):
        sftp_config['host'] = f"192.168.56.1{i}"
        sftp, transport = connect_to_sftp(
            sftp_config['host'],
            sftp_config['port'],
            sftp_config['username'],
            sftp_config['key_path']
        )
        log_lines = read_logs(sftp, sftp_config['remote_path'])
        for line in log_lines:
            if line != '':
                parsed_date, parsed_time, message = parse_raw_log_line(line)
                if parsed_date and message and parsed_time:
                    insert_raw_logs(cursor, parsed_date, parsed_time, message, 'raw_logs')
                else:
                    print(f"Failed to parse line: {line}")
        sftp.close()
        transport.close()
    db.commit()
finally:
    try:
        if cursor:
            cursor.close()
        if db:
            db.close()
    except Exception as e:
        print(f"Cleanup error: {e}")
    print("SFTP connection closed")