import flask
import time
import os
import urllib
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import BadRequest
from threading import Thread


app = flask.Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    html = db.Column(db.String)

    def execute(self):
        if self.completed:
            raise Exception('Error trying to execute already completed task: Job {}'.format(self.id))
        else:
            self.html = urllib.urlopen(self.url).read()
            self.completed = True
            db.session.commit()


class JobQueue():
    def __init__(self):
        self.queue = []

    def push(self, item):
        self.queue.append(item)

    def pop(self):
        if self.queue:
            item = self.queue[0]
            self.queue = self.queue[1:]
            return item
        else:
            return None

    def run(self):
        while True:
            time.sleep(1)
            queueHead = self.pop()
            if queueHead:
                queueHead.execute()


global_job_queue = JobQueue()


@app.route('/submit', methods=['POST'])
def submit():
    data = flask.request.get_data()
    if 'url' in data:
        new_job = Job(url=data['url'])
        db.session.add(new_job)
        db.session.commit()
        global_job_queue.push(new_job)
        return new_job.id
    else:
        raise BadRequest('POST payload must contain a "url" key.')


@app.route('/status', methods=['GET'])
def status():
    data = flask.request.args
    if 'jobId' in data:
        job_id = data['jobId']
        job_db_row = db.session.query(Job).get(job_id)
        if job_db_row and job_db_row.completed:
            return job_db_row.html
        else:
            return 'Job {} is incomplete'.format(job_id)
    else:
        raise BadRequest('GET payload must contain a "job_id" key.')


if __name__ == '__main__':
    Thread(target=(lambda: app.run(debug=True))).start()
    Thread(target=(lambda: global_job_queue.run())).start()
