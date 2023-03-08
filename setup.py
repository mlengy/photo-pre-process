from setuptools import setup

setup(
    name="photo-preprocess",
    description="Scripts to preprocess digital images for storage and editing",
    version="0.0.1",
    author="Michael Leng",
    author_email="michael@len.gy",
    install_requires=["typer[all]"],
    entry_points={
        "console_scripts": [
            "pp=pp:main"
        ]
    }
)