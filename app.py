import flask
import time
import os
import requests
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
        """
        Executes a given job: scrapes the HTML from the URL.
        Also handles erroneous URLs by setting the HTML field to an error message.
        """

        if self.completed:
            raise Exception('Error trying to execute already completed task: Job {}'.format(self.id))
        else:
            try:
                self.html = requests.get(self.url).text
            except Exception as e:
                self.html = "Could not retrieve HTML for URL. Error message: {}".format(e)

            self.completed = True
            db.session.commit()


class JobQueue():
    """
    Implements a FIFO queue.
    """

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
            # time.sleep(1) assumes that we're getting a low volume of requests, so we can let the processor idle.
            time.sleep(1)
            queueHead = self.pop()
            if queueHead:
                # it is necessary to use app.app_context() here because this is a multithreaded application.
                # (this thread could otherwise not access the db session, which runs single-threadedly.)
                with app.app_context():
                    item = db.session.query(Job).get(queueHead)
                    item.execute()


global_job_queue = JobQueue()


@app.route('/submit', methods=['POST'])
def submit():
    """
    Handle calls to the submit route. Assumes that the user passes a JSON blob
    with 'url' as a key and the url to scrape as a value.
    """

    data = flask.request.form
    if 'url' in data:
        new_job = Job(url=data['url'])
        db.session.add(new_job)
        db.session.commit()
        global_job_queue.push(new_job.id)
        return str(new_job.id)
    else:
        raise BadRequest('POST payload must contain a "url" key.')


@app.route('/status', methods=['GET'])
def status():
    """
    Handle calls to the status route. Assumes that the user passes a JSON blob
    with 'jobId' as a key and the id of the job as a value.
    """

    data = flask.request.args
    if 'jobId' in data:
        job_id = data['jobId']
        job_db_row = db.session.query(Job).get(job_id)
        if job_db_row:
            if job_db_row.completed:
                return job_db_row.html
            else:
                return 'Job {} is incomplete'.format(job_id)
        else:
            return "There is no Job with id {} in the Jobs database.".format(job_id)

    else:
        raise BadRequest('GET payload must contain a "job_id" key.')


if __name__ == '__main__':
    Thread(target=(lambda: app.run(debug=False))).start()
    Thread(target=(lambda: global_job_queue.run())).start()
