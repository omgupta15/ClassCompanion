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

    return flask.render_template("index.html", config = project)

@app.route("/getFilesList", methods = ["GET"])
@limiter.limit("5/second")
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
                            userKey
                        ) VALUES (%s, %s)
                    """,
                    (
                        int(time.time()*1000),
                        userKey,
                    )
                )
                database.commit()

        return flask.jsonify({
            "status": "not-found",
            "userKey": userKey
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
                            userKey
                        ) VALUES (%s, %s)
                    """,
                    (
                        int(time.time()*1000),
                        userKey,
                    )
                )
                database.commit()

        return flask.jsonify({
            "status": "not-found",
            "userKey": userKey
        })

    userId = result[0]

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id, name, created FROM Files WHERE userId = %s", (userId,))
            result = cursor.fetchall()

    return flask.jsonify({
        "status": "found",
        "files": [{"index": index+1, "fileId": fileId, "name": name, "created": created} for index, (fileId, name, created) in enumerate(result)]
    })

@app.route("/getFile", methods = ["POST"])
@limiter.limit("5/second")
def getFile():
    args = flask.request.args
    data = flask.request.get_data(as_text = True)
    headers = flask.request.headers
    cookies = flask.request.cookies
    method = flask.request.method
    ip = flask.request.remote_addr

    if headers.get("Host") != project["host"]:
        return flask.redirect(project["website"])

    if not cookies.get("userKey"):
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    try:
        data = json.loads(data)
        fileId = int(data["fileId"])
    except:
        return flask.jsonify({
            "success": False,
            "error": "invalid-json"
        }), 400

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id FROM Users WHERE userKey = %s", (cookies.get("userKey"),))
            result = cursor.fetchone()

    if not result:
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    userId = result[0]

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id, name, content FROM Files WHERE id = %s AND userId = %s", (fileId, userId,))
            result = cursor.fetchone()

        if not result:
            return flask.jsonify({
                "success": False,
                "error": "file-not-found"
            })

    return flask.jsonify({
        "success": True,
        "fileId": result[0],
        "name": result[1],
        "content": result[2]
    })

@app.route("/updateFile", methods = ["POST"])
@limiter.limit("5/second")
def updateFile():
    args = flask.request.args
    data = flask.request.get_data(as_text = True)
    headers = flask.request.headers
    cookies = flask.request.cookies
    method = flask.request.method
    ip = flask.request.remote_addr

    if headers.get("Host") != project["host"]:
        return flask.redirect(project["website"])

    if not cookies.get("userKey"):
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    try:
        data = json.loads(data)
        fileId = data["fileId"]
        name = str(data["name"])
        text = str(data["text"])
        if fileId != None:
            fileId = int(fileId)
    except:
        return flask.jsonify({
            "success": False,
            "error": "invalid-json"
        }), 400

    if not name:
        return flask.jsonify({
            "success": False,
            "error": "no-name"
        })

    if len(name) > 250:
        return flask.jsonify({
            "success": False,
            "error": "name-too-long"
        })

    if len(text) > 1000000:
        return flask.jsonify({
            "success": False,
            "error": "text-too-long"
        })

    with getDatabase() as database:
        with database.cursor() as cursor:
            cursor.execute("SELECT id FROM Users WHERE userKey = %s", (cookies.get("userKey"),))
            result = cursor.fetchone()

    if not result:
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    userId = result[0]
    
    if fileId == None:
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO Files (
                            userId,
                            name,
                            created,
                            content
                        ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        userId,
                        name,
                        int(time.time()*1000),
                        text
                    )
                )
                database.commit()

            with database.cursor() as cursor:
                cursor.execute("SELECT id FROM Files ORDER BY id DESC LIMIT 1")
                fileId = cursor.fetchone()[0]

    else:
        with getDatabase() as database:
            with database.cursor() as cursor:
                cursor.execute("SELECT id FROM Files WHERE id = %s AND userId = %s", (fileId, userId,))
                result = cursor.fetchone()

            if not result:
                return flask.jsonify({
                    "success": False,
                    "error": "file-not-found"
                })

            with database.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE Files
                        SET name = %s, content = %s
                        WHERE id = %s AND userId = %s
                    """,
                    (
                        name,
                        text,
                        fileId,
                        userId,
                    )
                )
                database.commit()

    return flask.jsonify({
        "success": True,
        "fileId": fileId
    })

generateKey = lambda size: "".join([random.choice(string.ascii_letters + string.digits + "_" + "-") for _ in range(size)])

app.run(port = 80, debug = True)

###########################################################################

# CREATING THE DATABASE:

# with getDatabase() as mysql:
#     with mysql.cursor() as cursor:
#         cursor.execute("CREATE DATABASE ClassCompanion")
#         mysql.commit()

###########################################################################

# CREATING THE TABLES:

# with getDatabase() as database:
#     with database.cursor() as cursor:
#         cursor.execute("DROP TABLE Users;")
#         database.commit()

#     with database.cursor() as cursor:
#         cursor.execute("""
#             CREATE TABLE Users (
#                 id BIGINT PRIMARY KEY AUTO_INCREMENT,
#                 created BIGINT, -- milliseconds
#                 userKey TEXT
#             )
#         """)
#         database.commit()

#     with database.cursor() as cursor:
#         cursor.execute("DROP TABLE Files;")
#         database.commit()
    
#     with database.cursor() as cursor:
#         cursor.execute("""
#             CREATE TABLE Files (
#                 id BIGINT PRIMARY KEY AUTO_INCREMENT,
#                 userId BIGINT,
#                 name TEXT,
#                 created BIGINT, -- milliseconds
#                 content LONGTEXT
#             )
#         """)
#         database.commit()


