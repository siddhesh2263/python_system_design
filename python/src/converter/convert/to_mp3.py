import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor
import pika.spec

def start(message, fs_videos, fs_mp3s, channel):
    
    # make it into a python object
    message = json.loads(message)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()

    # video contents
    # refer the code which uploaded the file.
    out = fs_videos.get(ObjectId(message["video_fid"]))

    # add video contents to empty file
    tf.write(out.read())

    # create audio from temp video file
    # tf.name abstracts the path at which the temp file is stored.
    audio = moviepy.editor.VideoFileClip(tf.name).audio

    tf.close()

    # temp file will be automatically deleted.

    # write audio to the file
    # no collisions with file names
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    # need to put this message on a different queue
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            # because we need to convert the python object into json:
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        # if the message is not being able to sent on the queue, we need
        # to delete the mp3 file from the database, because it won't be
        # processed.
        fs_mp3s.delete(fid)
        return "failed to publish message"


