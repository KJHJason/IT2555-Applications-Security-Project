import mysql.connector
from os import environ

def mysql_init_tables(debug:bool=False) -> mysql.connector.connection.MySQLConnection:
    """
    Initialize the database with the necessary tables

    Args:
        debug (bool): If true, will initialise locally, else will initialise remotely
    
    Returns:
        The connection to the database (mysql connection object)
    """
    if (debug):
        host = "localhost"
        password = environ["LOCAL_SQL_PASS"]
    else:
        host = "34.143.163.29" # Google Cloud SQL Public address
        password = environ["REMOTE_SQL_PASS"]
    
    mydb = mysql.connector.connect(
        host=host,
        user="root",
        password=password
    )

    cur = mydb.cursor()
    cur.execute("CREATE DATABASE coursefinity")
    mydb.commit()

    mydb.close()

    mydb = mysql.connector.connect(
        host=host,
        user="root",
        password=password,
        database="coursefinity"
    )
    cur = mydb.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS admin (
        id CHAR(32) PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE, 
        email VARCHAR(255) NOT NULL UNIQUE, 
        password VARCHAR(255) NOT NULL,
        account_creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user (
        id CHAR(32) PRIMARY KEY, 
        role VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL UNIQUE, 
        email VARCHAR(255) NOT NULL UNIQUE, 
        password VARCHAR(255), -- can be null for user who signed in using Google OAuth2
        profile_image VARCHAR(255), 
        date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        card_name VARCHAR(255),
        card_no INTEGER, -- May not be unique since one might have alt accounts.
        card_exp VARCHAR(255),
        cart_courses VARCHAR(255) NOT NULL,
        purchased_courses VARCHAR(255) NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS course (
        course_id CHAR(32) PRIMARY KEY, 
        teacher_id CHAR(32) NOT NULL,
        course_name VARCHAR(255) NOT NULL,
        course_description VARCHAR(255),
        course_image_path VARCHAR(255),
        course_price DECIMAL(6,2) NOT NULL, -- up to 6 digits, 2 decimal places (max: $9999.99)
        course_category VARCHAR(255) NOT NULL,
        course_total_rating INTEGER NOT NULL,
        course_rating_count INTEGER NOT NULL,
        date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        video_path VARCHAR(255) NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES user(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS twofa_token (
        token CHAR(32) PRIMARY KEY,
        user_id CHAR(32) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS login_attempts (
        user_id CHAR(32) PRIMARY KEY,
        attempts INTEGER NOT NULL,
        reset_date DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS session (
        session_id CHAR(32) PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        expiry_date DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS cart (
        user_id CHAR(32),
        course_id CHAR(32),
        PRIMARY KEY (user_id, course_id),
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (course_id) REFERENCES course(course_id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS purchased (
        user_id CHAR(32),
        course_id CHAR(32),
        PRIMARY KEY (user_id, course_id),
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (course_id) REFERENCES course(course_id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS review (
        user_id CHAR(32),
        course_id CHAR(32),
        course_rating INTEGER,
        review_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, course_id),
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (course_id) REFERENCES course(course_id)
    )""")

    mydb.commit()
    return mydb

if (__name__ == "__main__"):
    while (1):
        debugPrompt = input("Debug mode? (Y/n): ").lower().strip()
        if (debugPrompt not in ("y", "n", "")):
            print("Invalid input", end="\n\n")
            continue
        else:
            debugFlag = True if (debugPrompt != "n") else False
            break

    try:
        mysql_init_tables(debug=debugFlag)
        print("Successfully initialised the tables in the database, \"coursefinity\"!")
    except (mysql.connector.errors.ProgrammingError) as e:
        print("\nSyntax error caught!")
        print("More details:")
        print(e)

        from MySQL_reset import delete_mysql_database
        delete_mysql_database(debug=debugFlag)
        print("\nDeleted all tables as there was a syntax error in the schema.")