import unittest
import sys
import os


sys.path.append('..')

from exifread import process_file
from helpers.folder_helper import copy_test_images
from helpers.folder_helper import TEST_FOLDER
from helpers.folder_helper import delete_folder


class TestVideos(unittest.TestCase):
    def tearDown(self):
        delete_folder()

    # TODO: add a mp4 with exif tags
    def test_video_mp4(self):
        copy_test_images(file='test_video.mp4')
        with open(file=os.path.join(TEST_FOLDER, 'test_video.mp4'), mode='rb') as file: exif_tags = process_file(file)
        make = next((exif_tags[tag] for tag in exif_tags.keys() if 'Make' in tag), None)
        assert make is None

