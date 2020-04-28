from google.cloud import storage
import os


def upload_blob(source_file_name, bucket_name="mamba_songs_bucket",
                songs_dir="songs"):
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
