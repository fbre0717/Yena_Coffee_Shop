import os
import sys
import sqlite3
from flask import Flask, request, jsonify
from flask_jwt_extended import *
from google.cloud import dialogflow_v2 as dialogflow


app = Flask(__name__)

jwt = JWTManager(app)
project_id = 'newagent-tsnu'
session_id = 'newagent-tsnu'
language_code = 'en'

GOOGLE_AUTHENTICATION_FILE_NAME = "credentials/key.json"
current_directory = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

@app.route('/')
def hello_world():
    return('Hello')
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = sqlite3.connect("members.db")
    cur = conn.cursor()
    data = request.get_json(force=True)
    userId = data['userId']
    username = data['username']
    password = data['password']
    repassword = data['repassword']

    if not (userId and username and password and repassword):
        return jsonify(result="fail", error="please fill all blanks.")
    elif password != repassword:
        return jsonify(result="fail", error="Password check is incorrect.")
    else:
        cnt = cur.execute(
            "SELECT count(*) From User Where userid=?", (userId,)).fetchone()[0]
        if(cnt > 0):
            conn.commit()
            conn.close()
            return jsonify(result="fail", error="That ID is already taken.")
        else:
            cur.execute("Insert into User values (?, ?, ?)",
                        (userId, username, password))
            conn.commit()
            conn.close()
            return jsonify(result="success", token=userId)
            

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    conn = sqlite3.connect("members.db")
    cur = conn.cursor()
    data = request.get_json(force=True)
    userId = data['userId']
    password = data['password']
    query  ="SELECT * FROM User WHERE User.userid == \"" + userId + "\" AND User.password == \"" + password + "\""
    
    cur.execute(query)
    cnt = cur.fetchall()
    conn.commit()
    conn.close()
    if (len(cnt)!=0):
        return jsonify(result="success", token=userId)
    else:
        return jsonify(result="fail", error="ID or password is incorrect.")


@app.route('/message', methods=['GET', 'POST'])
def message():
    data = request.get_json(force=True)
    requesttext = data['message']['text']
    print(requesttext)
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=requesttext, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        
    reply = response.query_result.fulfillment_text
    
    print(reply)
    
    result = []
    result.append(reply)
    
    return jsonify(result="success", reply = result)


    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)












