import pika, json

import pika.spec

def upload(f, fs, channel, access):
    try:
        # first try to put the video in mongodb
        fid = fs.put(f)
    except Exception as err:
        print(err)
        # return "TRY 1 - internal server error | ", 500
        return str(err), 500
    
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            # empty exchange field means default.
            exchange="",
            routing_key="video",    # name of the queue
            body=json.dumps(message),    # opposite of json dumps
            properties=pika.BasicProperties(
                # when pod fails, the messages will be still there.
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        # delete the file from the mongodb, since it won't be processed in the future.
        print(err)
        fs.delete(fid)
        return "TRY 2 - internal server error", 500

