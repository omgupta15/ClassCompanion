import base64, json, os, math, threading, string, random, waitress
import flask, mysql.connector, flask_limiter, time, datetime
from flask_limiter.util import get_remote_address

os.system("title ClassCompanion Host")

def getDatabase():
    return mysql.connector.connect(
        host = "localhost",
        user = os.environ.get("MySQL_username"),
        passwd = os.environ.get("MySQL_password"),
        database = "ClassCompanion"
    )

app = flask.Flask(__name__, template_folder = ".", static_folder = "resources/")

# def get_remote_address():
#     return flask.request.headers.get("X-Real-IP") # Using proxy_pass in nginx & setting header for real ip.

limiter = flask_limiter.Limiter(app, key_func = get_remote_address)

project = {
    "name": "Class Companion",
    "website": "http://localhost/", #"http://classcompanion.us.to/",
    "host": "localhost", #"classcompanion.us.to",
    "ip": "0.0.0.0",
    "port": 80 # 1516
}

@app.route("/", methods = ["GET"])
@limiter.limit("5/second")
def index():
    args = flask.request.args
    data = flask.request.get_data(as_text = True)
    headers = flask.request.headers
    cookies = flask.request.cookies
    method = flask.request.method
    ip = flask.request.remote_addr

    if headers.get("Host") != project["host"]:
        return flask.redirect(project["website"])

    return flask.render_template("index.html")

@app.route("/getFilesList", methods = ["GET"])
@limiter.limit("1/second")
def getFilesList():
    args = flask.request.args
    data = flask.request.get_data(as_text = True)
    headers = flask.request.headers
    cookies = flask.request.cookies
    method = flask.request.method
    ip = flask.request.remote_addr

    if headers.get("Host") != project["host"]:
        return flask.redirect(project["website"])

    if not cookies.get("userKey"):
        userKey = generateKey(100)
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute("SELECT id FROM Users WHERE userKey = %s", (userKey,))
                result = cursor.fetchone()
        
        while result:
            userKey = generateKey(100)
            with getDatabase() as database:
                with database.cursor() as cursor:
                    cursor.execute("SELECT id FROM Users WHERE userKey = %s", (userKey,))
                    result = cursor.fetchone()
        
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO Users (
                            created,
                            key
                        ) VALUES (%s, %s)
                    """,
                    (int(time.time()*1000), userKey,)
                )
                database.commit()

        return flask.jsonify({
            "status": "not-found",
            "key": userKey
        })

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id FROM Users WHERE userKey = %s", (cookies.get("userKey"),))
            result = cursor.fetchone()

    if not result:
        userKey = generateKey(100)
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute("SELECT id FROM Users WHERE userKey = %s", (userKey,))
                result = cursor.fetchone()
        
        while result:
            userKey = generateKey(100)
            with getDatabase() as database:
                with database.cursor() as cursor:
                    cursor.execute("SELECT id FROM Users WHERE userKey = %s", (userKey,))
                    result = cursor.fetchone()
        
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO Users (
                            created,
                            key
                        ) VALUES (%s, %s)
                    """,
                    (int(time.time()*1000), userKey,)
                )
                database.commit()

        return flask.jsonify({
            "status": "not-found",
            "key": userKey
        })

    userId = result[0]

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT name, created FROM Files WHERE userId = %s", (userId,))
            result = cursor.fetchall()

    return flask.jsonify({
        "status": "found",
        "files": [{"name": name, "created": created} for name, created in result]
    })

@app.route("/updateFile", methods = ["POST"])
@limiter.limit("1/second")
def getFilesList():
    args = flask.request.args
    data = flask.request.get_data(as_text = True)
    headers = flask.request.headers
    cookies = flask.request.cookies
    method = flask.request.method
    ip = flask.request.remote_addr

    if headers.get("Host") != project["host"]:
        return flask.redirect(project["website"])

    if not cookies.get("userKey"):
        return flask.jsonify({"success": False})

    try:
        data = json.loads(data)
        name = data["name"]

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id FROM Users WHERE userKey = %s", (cookies.get("userKey"),))
            result = cursor.fetchone()

    if not result:
        return flask.jsonify({"success": False})

    userId = result[0]

def generateKey(size):
    return "".join([random.choice(string.ascii_letters + string.digits + "_" + "-") for _ in range(size)])

###########################################################################

# CREATING THE DATABASE:

# with getDatabase() as mysql:
#     with mysql.cursor() as cursor:
#         cursor.execute("CREATE DATABASE ClassCompanion")
#         mysql.commit()

###########################################################################

# CREATING THE TABLES:

with getDatabase() as database:
    with database.cursor() as cursor:
        cursor.execute("DROP TABLE Users;")
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE Users (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                created BIGINT,
                userKey TEXT
            )
        """)
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("DROP TABLE Files;")
        database.commit()
    
    with database.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE Files (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                userId BIGINT,
                name TEXT,
                created BIGINT,
                content LONGTEXT
            )
        """)
        database.commit()


