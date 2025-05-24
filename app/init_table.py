from sftp_log_reader import connect_to_mariadb, create_log_table

try:
    db = connect_to_mariadb()
    cursor = db.cursor()
    create_log_table(cursor)
    db.commit()
except Exception as e:
    print(f"Unexpected error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()