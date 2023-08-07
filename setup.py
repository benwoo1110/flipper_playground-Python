from pathlib import Path

from setuptools import setup, find_packages


setup(
    name="flipper_playground",
    version="0.1.0",
    url="https://github.com/benwoo1110/flipper_playground-Python",
    author="benwoo1110",
    author_email="wben1110@gmail.com",
    packages=find_packages(),
    python_requires=">=3.10",
    description="Code a simple Flipper app in Python!",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type='text/markdown',
    install_requires=(Path(__file__).parent / "requirements.txt").read_text().splitlines(),
    classifiers=[
        "Natural Language :: English",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
