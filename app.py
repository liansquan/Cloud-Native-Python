from time import strftime, gmtime

from flask import Flask, request
from flask import jsonify
from flask import abort
from flask import make_response
from flask import render_template
import json
import sqlite3

app = Flask(__name__)

#####################################################################################
@app.route("/api/v1/info")
def home_index():
    conn = sqlite3.connect("mydb.db")
    print("Opened database successfully")
    api_list = []
    cursor = conn.execute("select buildtime, version, methods, links from apirelease")
    for row in cursor:
        api = {}
        api['version'] = row[0]
        api['buildtime'] = row[1]
        api['methods'] = row[2]
        api['links'] = row[3]
        api_list.append(api)
    conn.close()
    return jsonify({'api_version': api_list}), 200

#######################################################################################
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()


def list_users():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    api_list = []
    cursor = conn.execute("SELECT username, full_name, emailid, password, id from users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['email'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    conn.close()
    return jsonify({'user_list': api_list})

#######################################################################################
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)


def list_user(user_id):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where id=?", (user_id,))
    data = cursor.fetchall()
    if not data:
        abort(404)
    user = {}
    if len(data) != 0:
        user['username'] = data[0][0]
        user['name'] = data[0][1]
        user['email'] = data[0][2]
        user['password'] = data[0][3]
        user['id'] = data[0][4]
        conn.close()
        return jsonify(user)

#######################################################################################
@app.route('/api/v1/users', methods=['POST'])
def create_user():
    data_json = request.form.to_dict()
    # print(data)
    if not data_json or 'username' not in data_json or 'email' not in data_json or 'password' not in data_json:
        abort(400)
    user = {
        'username': data_json['username'],
        'email': data_json['email'],
        'name': data_json.get('name', ""),
        'password': data_json['password']
    }
    return jsonify({'status': add_user(user)}), 201


def add_user(user):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=? or emailid=?", (user['username'], user['email']))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute("Insert into users (username, emailid, password, full_name) values(?,?,?,?)", (user['username'],
                        user['email'], user['password'], user['name']))
        conn.commit()
        conn.close()
        return "Success"
    conn.close()
    return "Error"

#######################################################################################
@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    data_json = request.form.to_dict()
    if not data_json or 'username' not in data_json:
        abort(400)
    user = data_json['username']
    return jsonify({'status': del_user(user)}), 200


def del_user(del_user):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=?", (del_user,))
    data = cursor.fetchall()
    print("Data: ", data)
    if len(data) == 0:
        abort(404)
    else:
        cursor.execute("delete from users where username==?", (del_user,))
        conn.commit()
        conn.close()
        return "Success"

#######################################################################################
@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data_json = request.form.to_dict()
    if not data_json:
        abort(400)
    user = {}
    user['id'] = user_id
    key_list = data_json.keys()
    for i in key_list:
        user[i] = data_json[i]
    print(user)
    return jsonify({'status': upd_user(user)}), 200


def upd_user(user):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where id=?", (user['id'],))
    data = cursor.fetchall()
    print('Data:', data)
    if len(data) == 0:
        abort(404)
    else:
        keys = user.keys()
        for i in keys:
            if i != 'id':
                cursor.execute("UPDATE users set {0}=? where id=?".format(i), (user[i], user['id']))
                conn.commit()
        conn.close()
        return "Success"

##############################################################################
@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
    return list_tweets()


def list_tweets():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT username, body, tweet_time, id from tweets")
    data = cursor.fetchall()
    api_list = []
    if len(data) != 0:
        for row in data:
            tweet = {}
            tweet['Tweet By'] = row[0]
            tweet['Body'] = row[1]
            tweet['Timestamp'] = row[2]
            tweet['id'] = row[3]
            api_list.append(tweet)
    conn.close()
    return jsonify({'tweets_list': api_list})

#######################################################################################
@app.route('/api/v2/tweets', methods=['POST'])
def add_tweets():
    data_json = request.form.to_dict()
    if not data_json or 'username' not in data_json or 'body' not in data_json:
        abort(400)
    user_tweet = {}
    user_tweet['username'] = data_json['username']
    user_tweet['body'] = data_json['body']
    user_tweet['created_at'] = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
    return jsonify({'status': add_tweet(user_tweet)}), 200


def add_tweet(user_tweet):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=?", (user_tweet['username'],))
    data = cursor.fetchall()
    if len(data) == 0:
        abort(404)
    else:
        cursor.execute("INSERT into tweets (username, body, tweet_time) values(?,?,?)", (user_tweet['username'],
                                                            user_tweet['body'], user_tweet['created_at']))
        conn.commit()
        conn.close()
        return "Success"

#######################################################################################
@app.route('/api/v2/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
    return list_tweet(id)


def list_tweet(user_id):
    print(user_id)
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully")
    cursor = conn.cursor()
    cursor.execute("SELECT * from tweets where id=?", (user_id,))
    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        user = {}
        user['id'] = data[0][0]
        user['username'] = data[0][1]
        user['body'] = data[0][2]
        user['tweet_time'] = data[0][3]
    conn.close()
    return jsonify(user)


@app.route('/adduser')
def adduser():
    return render_template('adduser.html')

#######################################################################################
#######################################################################################
@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
