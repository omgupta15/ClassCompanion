import base64, json, os, math, threading, string, random
import flask, sqlite3, time, datetime

def getDatabase():
    return sqlite3.connect("local.db")

app = flask.Flask(__name__, template_folder = ".", static_folder = "resources/")

project = {
    "name": "Class Companion",
    "website": "http://localhost/",
    "host": "localhost",
    "ip": "0.0.0.0",
    "port": 80
}

@app.route("/", methods = ["GET"])
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
            cursor = database.cursor()
            cursor.execute("SELECT id FROM Users WHERE userKey = ?", (userKey,))
            result = cursor.fetchone()
        
        while result:
            userKey = generateKey(100)
            with getDatabase() as database:
                cursor = database.cursor()
                cursor.execute("SELECT id FROM Users WHERE userKey = ?", (userKey,))
                result = cursor.fetchone()
        
        with getDatabase() as database:
            cursor = database.cursor()
            cursor.execute(
                """
                    INSERT INTO Users (
                        created,
                        userKey
                    ) VALUES (?, ?)
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
        cursor = database.cursor()
        cursor.execute("SELECT id FROM Users WHERE userKey = ?", (cookies.get("userKey"),))
        result = cursor.fetchone()

    if not result:
        userKey = generateKey(100)
        with getDatabase() as database:
            cursor = database.cursor()
            cursor.execute("SELECT id FROM Users WHERE userKey = ?", (userKey,))
            result = cursor.fetchone()
        
        while result:
            userKey = generateKey(100)
            with getDatabase() as database:
                cursor = database.cursor()
                cursor.execute("SELECT id FROM Users WHERE userKey = ?", (userKey,))
                result = cursor.fetchone()
        
        with getDatabase() as database:
            cursor = database.cursor()
            cursor.execute(
                """
                    INSERT INTO Users (
                        created,
                        userKey
                    ) VALUES (?, ?)
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
        cursor = database.cursor()
        cursor.execute("SELECT id, name, created FROM Files WHERE userId = ?", (userId,))
        result = cursor.fetchall()

    return flask.jsonify({
        "status": "found",
        "files": [{"index": index+1, "fileId": fileId, "name": name, "created": created} for index, (fileId, name, created) in enumerate(result)]
    })

@app.route("/getFile", methods = ["POST"])
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
        cursor = database.cursor()
        cursor.execute("SELECT id FROM Users WHERE userKey = ?", (cookies.get("userKey"),))
        result = cursor.fetchone()

    if not result:
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    userId = result[0]

    with getDatabase() as database:
        cursor = database.cursor()
        cursor.execute("SELECT id, name, content FROM Files WHERE id = ? AND userId = ?", (fileId, userId,))
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
        cursor = database.cursor()
        cursor.execute("SELECT id FROM Users WHERE userKey = ?", (cookies.get("userKey"),))
        result = cursor.fetchone()

    if not result:
        return flask.jsonify({
            "success": False,
            "error": "user-not-found"
        })

    userId = result[0]

    if fileId == None:
        with getDatabase() as database:
            cursor = database.cursor()
            cursor.execute(
                """
                    INSERT INTO Files (
                        userId,
                        name,
                        created,
                        content
                    ) VALUES (?, ?, ?, ?)
                """,
                (
                    userId,
                    name,
                    int(time.time()*1000),
                    text
                )
            )
            database.commit()

            cursor = database.cursor()
            cursor.execute("SELECT id FROM Files ORDER BY id DESC LIMIT 1")
            fileId = cursor.fetchone()[0]

    else:
        with getDatabase() as database:
            cursor = database.cursor()
            cursor.execute("SELECT id FROM Files WHERE id = ? AND userId = ?", (fileId, userId,))
            result = cursor.fetchone()

            if not result:
                return flask.jsonify({
                    "success": False,
                    "error": "file-not-found"
                })

            cursor = database.cursor()
            cursor.execute(
                """
                    UPDATE Files
                    SET name = ?, content = ?
                    WHERE id = ? AND userId = ?
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

@app.route("/<url>")
def github(url):
    # For making these URLs Case-Insensitive
    url = url.lower()

    if url == "github":
        return flask.redirect("https://github.com/omgupta15/Code-Innovation-Series-ChitkaraUniversity", code = 301)

    if url in ("ppt", "presentation",):
        with open("Byte Coder-ClassCompanion-IncubatedInd-Presentation.pdf", "rb") as f:
            content = f.read()
        response = flask.make_response(content, 200)
        response.headers["Content-type"] = "application/pdf"
        response.headers["Content-disposition"] = "inline; filename=Byte Coder-ClassCompanion-IncubatedInd-Presentation.pdf"
        return response

    return flask.abort(404)

generateKey = lambda size: "".join([random.choice(string.ascii_letters + string.digits + "_" + "-") for _ in range(size)])

app.run(port = 80)
# waitress.serve(app, host = project["ip"], port = project["port"])

###########################################################################

# CREATING THE TABLES: (Created these tables in local.db file already.)

# with getDatabase() as database:
#     cursor = database.cursor()
#     cursor.execute("""
#         CREATE TABLE Users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             created INTEGER, -- milliseconds
#             userKey TEXT
#         )
#     """)
#     database.commit()
#     cursor = database.cursor()
#     cursor.execute("""
#         CREATE TABLE Files (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             userId INTEGER,
#             name TEXT,
#             created INTEGER, -- milliseconds
#             content TEXT
#         )
#     """)
#     database.commit()
