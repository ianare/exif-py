import os
import shutil
from pathlib import Path

TEST_FOLDER = '.test_folder'
TEST_IMAGES = os.path.join('tests', 'test_files')


def create_file(file):
  Path(os.path.join(TEST_FOLDER, file)).touch()


def delete_folder():
  shutil.rmtree(TEST_FOLDER, ignore_errors=True)


def copy_test_images(file:str):
  delete_folder()
  os.mkdir(TEST_FOLDER)
  if file:
      shutil.copy(src=os.path.join(TEST_IMAGES, file), dst=os.path.join(TEST_FOLDER, file))
  else:
    shutil.copy(src=os.path.join(TEST_IMAGES, os.path.sep), dst=TEST_FOLDER)


