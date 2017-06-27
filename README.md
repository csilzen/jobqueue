## Run Instructions

1. To install all required dependencies, run `pip install -r requirements.txt`
2. To set up the database, run `python2.7 db_setup.py`
3. To run the server itself, run `python2.7 app.py`

## Testing Instructions

The user can submit data to the `status` (GET) and `submit` (POST) routes, which take
JSON objects. When running the server (assumed to be on `127.0.0.1:5000`), 
you can use the Python REPL, curl, etc.
to send HTTP requests. Here are some examples of correct use:

- `requests.post("http://127.0.0.1:5000/submit", data={"url": "http://google.com"})`
- `requests.get("http://127.0.0.1:5000/status", params={"jobId": "5"})`

The content of these responses (i.e. the `jobId` returned by `submit` or the HTML returned
by `status`) can be accessed with `.content` like this:

```
>>> requests.post("http://127.0.0.1:5000/submit", data={"url": "http://wikipedia.org"}).content
'4'
```

## Implementation notes

This is a lightweight Python2.7 Flask application that implements a webserver
with `status` and `submit` routes. When the user sends data to the `submit` route,
a job is created in our database, and is pushed to the JobQueue. 

The webserver runs on one thread, the JobQueue runs on another -- the JobQueue
perpetually checks for items in the queue (currently at an arbitrary interval
of every second), and if there is an item in the queue, it scrapes the HTML
for the url of that job, and saves the result to that job's database row.

It'd be possible to build this application without multithreading, but the
multithreaded approach has two nice properties:

1. Having two separate threads reflects the traditional webserver/worker architecture, where
    each is a different machine. It was my impression that this was the spirit of the exercise.

2. The exercise demanded a Job Queue, and (erring on the side of caution) I implemented
    the queue as strict FIFO, which is easy when the entire queue runs on its own thread. (As opposed to
    having the webserver kick off a separate thread for each incoming submission.)
