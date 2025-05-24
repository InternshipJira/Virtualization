from sftp_log_reader import connect_to_sftp, read_logs, parse_log_line, connect_to_mariadb, insert_log
import os

sftp_config = {
    'host': os.getenv('SFTP_HOST'), 
    'port': int(os.getenv('SFTP_PORT', 22)),
    'username': os.getenv('SFTP_USERNAME'),
    'key_path': os.getenv('SFTP_KEY_PATH'),
    'remote_path': "uploads/alpine.log"
}
db = connect_to_mariadb()
cursor = db.cursor()
try:
    
    for i in range(1,4):
        sftp_config['remote_path'] = f"uploads/alpine{i}.log"
        sftp_config['host'] = f"192.168.56.1{i}"
        sftp, transport = connect_to_sftp(
            sftp_config['host'],
            sftp_config['port'],
            sftp_config['username'],
            sftp_config['key_path']
        )
        log_lines = read_logs(sftp, sftp_config['remote_path'])
        print(f"Alpine{i} log lines:")
        for line in log_lines:
            if line != '':
                parsed_date, parsed_time, ip_address = parse_log_line(line)
                if parsed_date and ip_address and parsed_time:
                    insert_log(cursor, parsed_date, parsed_time, ip_address, sftp_config['host'], 'sftp_logs')
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