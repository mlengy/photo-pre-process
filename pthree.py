from typing import Optional
import typer

from process import Process
from rename import Rename
from texif import Texif
from exif import Exif


app = typer.Typer()


@app.command(help="Renames, generates text EXIF, and generates EXIF files for photos")
def process(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process"
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output result of processing"
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="Extension of files to process"
        )
):
    Process(directory, output_directory, extension).process()


@app.command(help="Rename photos to a consistent format")
def rename(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process"
        ),
        in_place: bool = typer.Option(
            True,
            help="Rename original files without making a copy"
        ),
        skip_invalid: bool = typer.Option(
            False,
            help="Soft skip files that cannot be renamed"
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="Extension of files to process"
        )
):
    Rename(directory, in_place, skip_invalid, extension).rename()


@app.command(help="Generates text EXIF files for photos")
def texif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process"
        ),
        type: Optional[str] = typer.Option(
            "both",
            help="The type of texif: simple, full, or both"
        ),
        level: Optional[int] = typer.Option(
            3,
            help="Level of generated text EXIF data to use"
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="Extension of files to process"
        )
):
    Texif(directory, type, level, extension).texif()


@app.command(help="Generates EXIF files for photos")
def exif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process"
        ),
        level: Optional[int] = typer.Option(
            2,
            help="Level of generated EXIF data to use"
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="Extension of files to process"
        )
):
    Exif(directory, level, extension).exif()


def main():
    app()


if __name__ == "__main__":
    main()
