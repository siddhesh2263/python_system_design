import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

# COMMENTED OLD CODE
# # server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"
# # changed configuration to localhost settings.
# server.config["MONGO_URI"] = "mongodb://0.0.0.0:27017/videos"

# now we need to use the both databases - mp3s and videos

# COMMENTED OLD CODE
# # PyMongo abstracts the mongodb connections.
# mongo = PyMongo(server)

# we need 2 instances for the separate databases:
mongo_video = PyMongo(
    server,
    uri="mongodb://0.0.0.0:27017/videos"
)

mongo_mp3 = PyMongo(
    server,
    uri="mongodb://0.0.0.0:27017/mp3s"
)


# COMMENTED OLD CODE
# # for memory optimization, sharding related. it divides files into parts or chunks.
# # pass the database from the mongo instance.
# fs = gridfs.GridFS(mongo.db)

# Now we need 2 gridfs instances:
fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# make connection with the RabbitMQ queue synchronous
# will be using rabbitmq as a stateful set in the kubernetes cluster
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    # needs to return a tuple
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err
        
        return "success!", 200
    else:
        return "GATEWAY not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            return f'internal server error - {str(err)}', 500
    
    return "download - not authorized", 401


if __name__ == "__main__":
    server.debug = True
    server.run(host="0.0.0.0", port=8080)