from setuptools import setup

setup(
    name="photo-pre-process",
    description="Scripts to pre-process digital images for storage and editing.",
    version="0.1.4",
    author="Michael Leng",
    author_email="michael@len.gy",
    url="https://len.gy",
    install_requires=[
        "typer[all]",
        "rich"
    ],
    license="MIT",
    entry_points={
        "console_scripts": [
            "pthree=pthree:main"
        ]
    }
)
