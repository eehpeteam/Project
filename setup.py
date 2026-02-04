"""Setup script for Teams Meeting Audio to Notes"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="teams-meeting-notes",
    version="1.0.0",
    author="Santhosh Nair",
    author_email="santhosh.s1@speridian.com",
    description="Capture Teams meeting audio, transcribe, and email notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanairgitrepo/MeetingNotes",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sounddevice==0.4.6",
        "numpy==1.26.4",
        "azure-cognitiveservices-speech==1.37.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "email-validator==2.1.0",
        "python-docx==0.8.11",
    ],
    entry_points={
        "console_scripts": [
            "teams-notes=main:main",
        ],
    },
)
