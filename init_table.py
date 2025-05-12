from sftp_log_reader import connect_to_mariadb, create_log_table

db = connect_to_mariadb()
cursor = db.cursor()
create_log_table(cursor)
try:
    db = connect_to_mariadb()
    cursor = db.cursor()
    create_log_table(cursor)
    db.commit()
finally:
    cursor.close()
    db.close()