import unittest
import sys
import os


sys.path.append('..')

from exifread import process_file
from helpers.folder_helper import copy_test_images
from helpers.folder_helper import TEST_FOLDER
from helpers.folder_helper import delete_folder


class TestMobiles(unittest.TestCase):
    def tearDown(self):
        delete_folder()

    def test_samsung(self):
        copy_test_images(file='samsung_a54_001.jpg')
        with open(file=os.path.join(TEST_FOLDER, 'samsung_a54_001.jpg'), mode='rb') as file: exif_tags = process_file(file)
        make = next((exif_tags[tag] for tag in exif_tags.keys() if 'Make' in tag), None)
        assert str(make) == 'samsung'

    def test_apple(self):
        copy_test_images(file='iphone_x_001.jpeg')
        with open(file=os.path.join(TEST_FOLDER, 'iphone_x_001.jpeg'), mode='rb') as file: exif_tags = process_file(file)
        make = next((exif_tags[tag] for tag in exif_tags.keys() if 'Make' in tag), None)
        assert str(make) == 'Apple'


class TestCameras(unittest.TestCase):
    def tearDown(self):
        delete_folder()

    def test_sony_jpg(self):
        copy_test_images(file='sony_alpha_a58.JPG')
        with open(file=os.path.join(TEST_FOLDER, 'sony_alpha_a58.JPG'), mode='rb') as file: exif_tags = process_file(file)
        make = next((exif_tags[tag] for tag in exif_tags.keys() if 'Make' in tag), None)
        assert str(make) == 'SONY'

    def test_sony_raw(self):
        copy_test_images(file='sony_alpha_a7iii_raw_image.ARW')
        with open(file=os.path.join(TEST_FOLDER, 'sony_alpha_a7iii_raw_image.ARW'), mode='rb') as file: exif_tags = process_file(file)
        make = next((exif_tags[tag] for tag in exif_tags.keys() if 'Make' in tag), None)
        assert str(make) == 'SONY'
