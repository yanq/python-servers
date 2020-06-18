#!/usr/bin/env python

from flask import Flask
from pymongo import MongoClient
from redis import Redis

app = Flask(__name__)

client = MongoClient("mongo:27017")
redis = Redis(host='redis', port=6379)


@app.route('/')
def todo():
    try:
        client.admin.command('ismaster')
    except:
        return "Server not available"

    return f"Hello from the MongoDB & Redis ! \n Hits: {redis.incr('hits')}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
