
from setuptools import setup, find_packages
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='swimp3',
    version='0.1',
    packages=find_packages(),
    py_modules=['swimp3'],
    entry_points={
        'console_scripts': [
            'swimp3 = swimp3.swimp3:swimp3'
        ]
    },
    install_requires=[requirements],
    author='Noah Florin',
    author_email='n.fs@hotmail.co.uk',
    description='Create and/or download a Spotify playlist',
    url='https://github.com/nfs002/swimp3',
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
)
