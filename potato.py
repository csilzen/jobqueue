import flask
import time
import os
from flask_sqlalchemy import SQLAlchemy


app = flask.Flask('grapes')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False),
    html = db.Column(db.String)

    def execute(self):
        pass


class JobQueue():
    def __init__():
        self.queue = []

    def push(self, item):
        self.queue.append(item)

    def pop(self):
        if self.queue:
            item = self.queue[0]
            self.queue = self.queue[1:]
        else:
            return None

    def run(self):
        while True:
            time.sleep(1)
            queueHead = self.pop()
            if queueHead:
                queueHead.execute()


@app.route('/blueberry')
def blueberry():
    return 'hello'


@app.route('/raspberry')
def raspberry():
    print(flask.request.args)
    return 'foo'


@app.route('/submit', methods=['POST'])
def submit():
    pass


@app.route('/status', methods=['GET'])
def status():
    data = flask.request.args
    if 'jobId' in data:
        

if __name__ == '__main__':
    app.run(debug=True)