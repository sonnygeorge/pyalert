from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

VERSION = "0.0.2"
DESCRIPTION = (
    "a framework to help you stay on top of what data is flowing through your code."
)


setup(
    name="pyalert",
    version=VERSION,
    author="Sonny George",
    author_email="<sonnygeorge5@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=["tests*"]),
    install_requires=[],
    keywords=["python", "runtime", "alerts"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
