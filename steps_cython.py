#step 1
#open in git bash and run this command to convert .py files into .pyx

find ./management ./timeman -name "*.py" -not -path "./*/migrations/*" -exec sh -c 'mv "$0" "${0%.py}.pyx"' {} \;



#step 2
#make a setup.py file in he root directiory and remember to change database scripts in views and urls.py in timeman to change to .py again before running this.
#run this file.
#if any import cython error uninstall cython and install again

from setuptools import setup, Extension
from Cython.Build import cythonize
import os

excluded_folders = {"timeenv", "build", "__pycache__", "tests"}
extensions = []

for root, dirs, files in os.walk("."):
    # Modify dirs in-place to skip excluded folders
    dirs[:] = [d for d in dirs if d not in excluded_folders]

    for file in files:
        if file.endswith(".pyx"):
            file_path = os.path.join(root, file)
            module_name = os.path.splitext(file_path)[0].replace(os.path.sep, ".").lstrip(".")
            extensions.append(Extension(module_name, [file_path]))

setup(
    ext_modules=cythonize(extensions, language_level="3"),
)


#step 3
#run this

python setup.py build_ext --inplace


#step 4
#to delete all pyx or c files run this, change the .c to .pyx for pyx files

find . -name "*.c" -type f -delete 









