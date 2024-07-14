import MySQLdb
import MySQLdb.cursors

# Database configuration
db_config = {
    'user': 'root',
    'password': 'newpassword',
    'host': 'localhost',
    'database': 'speaker_verification'
}

# Function to simulate loading users from the database
def get_govornici():
    try:
        connection = MySQLdb.connect(
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['password'],
            db=db_config['database'],
            cursorclass=MySQLdb.cursors.DictCursor
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM govornici")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except MySQLdb.Error as err:
        print(f"Error: {err}")
        return []


def get_govornici():
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM govornici")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching govornici: {str(e)}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_govornik_by_id(user_id):
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM govornici WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(f"Error fetching govornik by id: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_govornik(ime, prezime):
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO govornici (ime, prezime) VALUES (%s, %s)", (ime, prezime))
        connection.commit()
    except Exception as e:
        print(f"Error inserting govornik: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def update_govornik(user_id, ime, prezime):
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("UPDATE govornici SET ime = %s, prezime = %s WHERE id = %s", (ime, prezime, user_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating govornik: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def delete_govornik(user_id):
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM govornici WHERE id = %s", (user_id,))
        connection.commit()
    except Exception as e:
        print(f"Error deleting govornik: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def update_govornik_spektrogram(user_id, spectrogram_path):
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("UPDATE govornici SET spektrogram_url = %s WHERE id = %s", (spectrogram_path, user_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating govornik spektrogram URL: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def get_last_inserted_user_id():
    try:
        connection = MySQLdb.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]
        return user_id
    except Exception as e:
        print(f"Error fetching last inserted user id: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()
