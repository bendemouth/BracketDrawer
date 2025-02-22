from setuptools import setup, find_packages

setup(
    name='BracketDrawer',
    version='0.1.3.1',
    author="Ben DeMouth",
    author_email="bendemouth@gmail.com",
    url="https://github.com/bendemouth/BracketDrawer",
    description="A Python Package to easily create tournament brackets",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires=[
        'matplotlib',
        'pandas'
    ]
)
