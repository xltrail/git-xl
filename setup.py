"""Install git-xl as a python package"""
from distutils.core import setup

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

# Load __version__ info:
exec(open("src/version.py").read())

setup(
    name="gitxl",
    version=__version__,
    author="Felix Zumstein",
    author_email="felix.zumstein@zoomeranalytics.com",
    description="A Git Extension for Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xlwings/git-xl",
    # Get install requires from requirements.txt:
    install_requires=open("requirements.txt").read().splitlines(),
    packages=["gitxl"],
    package_dir={"gitxl": "src"},
    python_requires=">=3.7",
)
