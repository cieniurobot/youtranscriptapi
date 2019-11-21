from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_jwt import JWT, jwt_required
from werkzeug.security import safe_str_cmp


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'test', 'test'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


application = Flask(__name__)

application.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(application, authenticate, identity)


@application.route('/')
def index():
    return 'Welcome in Youtube transcript api!'


@application.route('/transcript/<movie_id>', methods=['GET'])
@jwt_required()
def transcript(movie_id: str):
    data = YouTubeTranscriptApi.get_transcript(movie_id)
    return jsonify(data)
