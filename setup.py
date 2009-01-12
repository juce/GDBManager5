# setup.py
from distutils.core import setup
import py2exe

setup(windows=["GDBManager.py"],
        data_files=[
            (".",[
                "default.png","shorts-mask.png","shorts63-mask.png",
                "wizard.png","converter.txt"]),
            ("docs",[
                "docs/README.txt"])
        ]
)
