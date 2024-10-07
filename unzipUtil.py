import os
import io
import zipfile
import re
import glob

def extract(filename):
    z = zipfile.ZipFile(filename)
    for f in z.namelist():
        # get directory name from file
        dirname = os.path.splitext(f)[0]
        # print(f)
        # create new directory
        os.mkdir(dirname)  
        # read inner zip file into bytes buffer 
        content = io.BytesIO(z.read(f))
        zip_file = zipfile.ZipFile(content)
        for i in zip_file.namelist():
            try:
                zip_file.extract(i, dirname)
            except Exception as e:
                print(e)


def list_zip_files(directory):
  """Lists all zip files in the specified directory.

  Args:
    directory: The directory to search in.

  Returns:
    A list of zip file names.
  """
  zip_files = glob.glob(os.path.join(directory, '*.zip'))
  return zip_files

# Example usage for /tmp/
zip_files_in_tmp = list_zip_files('/tmp')

for zip_file in zip_files_in_tmp:
    print(F'name of the zip file {zip_file}')
    extract(zip_file)
