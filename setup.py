from setuptools import setup, find_packages
 
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setup(
    name="dbesg",
    version="0.0.10",
    author="Lee Sang Jin",
    author_email="lee3jjang@gmail.com",
    description="Economic Scenario Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lee3jjang/dbesg",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)