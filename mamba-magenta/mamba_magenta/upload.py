from google.cloud import storage
import os
import const as C
import requests
import json


def upload_blob(source_file_name, request_dict,
                bucket_name="mamba_songs_bucket", songs_dir="songs"):
    """
    Uploads a file to the bucket.
    """
    # local path on the machine that generated the music.
    full_local_path = os.path.join(songs_dir, source_file_name)
    destination_blob_name = source_file_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(full_local_path)
    print(f"File {full_local_path} uploaded to {destination_blob_name}")

    # do put request
    api_link = C.SONGS_ENDPOINT
    print(request_dict)
    data = json.dumps(request_dict)
    response = requests.put(api_link, data=data)
    if response.status_code == 200:
        print("Successfully uploaded metadata!")
    # also upload file
