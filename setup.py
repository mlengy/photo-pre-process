from setuptools import setup

setup(
    name="photo-preprocess",
    description="Scripts to preprocess digital images for storage and editing",
    version="0.0.1",
    author="Michael Leng",
    author_email="michael@len.gy",
    install_requires=["typer[all]"],
    license="MIT",
    entry_points={
        "console_scripts": [
            "pthree=pthree:main"
        ]
    }
)