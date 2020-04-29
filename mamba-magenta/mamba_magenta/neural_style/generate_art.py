import tensorflow as tf
import os
import uuid

import matplotlib.pyplot as plt
import tensorflow_hub as hub
import matplotlib as mpl
mpl.rcParams['figure.figsize'] = (12, 12)
mpl.rcParams['axes.grid'] = False

import numpy as np
import PIL.Image
import time
import functools

import boto3

from boto3.dynamodb.conditions import Key, Attr

from google.cloud import storage

tf.compat.v1.enable_eager_execution()


class MambaArtGeneration():
    def __init__(self):
        content_pics = os.listdir('content')
        style_pics = os.listdir('style')
        # get absolute paths of images
        self.content = self.get_full_paths_list(content_pics, 'content')
        self.style = self.get_full_paths_list(style_pics, 'style')
        self.hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')
        dynamo = boto3.resource('dynamodb')
        self.table = dynamo.Table('songs')

    def get_full_paths_list(self, pic_names, root_folder):
        cwd = os.getcwd()
        for idx, pic_name in enumerate(pic_names):
            full_path = os.path.join(cwd, root_folder, pic_name)
            pic_names[idx] = full_path
        return pic_names

    def tensor_to_image(self, tensor):
        tensor = tensor*255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor) > 3:
            assert tensor.shape[0] == 1
        tensor = tensor[0]
        return PIL.Image.fromarray(tensor)

    def load_img(self, path_to_img):
        max_dim = 512
        img = tf.io.read_file(path_to_img)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)

        shape = tf.cast(tf.shape(img)[:-1], tf.float32)
        long_dim = max(shape)
        scale = max_dim / long_dim

        new_shape = tf.cast(shape * scale, tf.int32)

        img = tf.image.resize(img, new_shape)
        img = img[tf.newaxis, :]
        return img

    def imshow(self, image, title=None):
        image = self.squeeze(image)
        plt.imshow(image)
        if title:
            plt.title(title)

    def show_random_images(self):
        random_content = np.random.choice(self.content)
        random_style = np.random.choice(self.style)
        random_content_image = self.load_img(random_content)
        random_style_image = self.load_img(random_style)

        # plot the images
        plt.subplot(1, 2, 1)
        self.imshow(random_content_image, 'Content Image')

        plt.subplot(1, 2, 2)
        self.imshow(random_style_image, 'Style Image')
        plt.show()

    def squeeze(self, image):
        if len(image.shape) > 3:
            image = tf.squeeze(image, axis=0)
        return image

    def generate(self, content, random_style, verbose=False):
        # generate the model!
        content_image = self.load_img(content)
        style_image = self.load_img(random_style)
        stylized_image = self.hub_module(tf.constant(content_image),
                                         tf.constant(style_image))[0]
        result = self.tensor_to_image(stylized_image)
        if verbose:
            content = self.squeeze(content_image)
            style = self.squeeze(style_image)

            f, axarr = plt.subplots(3, 1)
            axarr[0].imshow(content)
            axarr[1].imshow(style)
            axarr[2].imshow(result)
            plt.show()
        return result

    def scan_db(self):
        response = self.table.scan()
        items = response['Items']
        return items

    def generate_all(self):
        os.makedirs('generated', exist_ok=True)

        items = self.scan_db()

        for idx, item in enumerate(items):
            random_style = np.random.choice(self.style)
            print(item)
            content = self.content[idx]
            print(content)
            print("At idx", idx)
            img = self.generate(content, random_style)
            art_id = str(uuid.uuid1())
            song_id = item['SongId']
            self.send_put_request(song_id, art_id)

            img.save(f"generated/{art_id}.png", "PNG")
            self.upload_blob(f"{art_id}.png")

    def upload_blob(self, source_file_name, bucket_name="mamba_songs_bucket",
                    songs_dir="generated"):
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

    def send_put_request(self, song_id, art_id):
        self.table.update_item(
            Key={
                'SongId': song_id
            },
            UpdateExpression='SET ArtId = :val1',
            ExpressionAttributeValues={
                ':val1': art_id
            }
        )


if __name__ == '__main__':
    art_generator = MambaArtGeneration()
    # art_generator.show_random_images()
    art_generator.generate_all()

