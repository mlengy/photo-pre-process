from typing import Optional

import typer

from commands.exif import Exif
from commands.process import Process
from commands.rename import Rename
from commands.texif import Texif, Preset, TexifType, TexifLevel

app = typer.Typer()


@app.command(help="Renames photos, generates text EXIF, and generates EXIF files.")
def process(
        initials: str = typer.Argument(
            ...,
            help="Your initials to prefix renamed files with."
        ),
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of processing."
        ),
        keep_original: bool = typer.Option(
            False,
            help="Leave original files untouched, copy then rename."
        ),
        preset: Optional[Preset] = typer.Option(
            Preset.fujifilmxt5,
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="The extension of files to process."
        )
):
    Process(initials, directory, output_directory, keep_original, preset, extension).process()


@app.command(help="Rename photos into a consistent format.")
def rename(
        initials: str = typer.Argument(
            ...,
            help="Your initials to prefix renamed files with."
        ),
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of renaming."
        ),
        keep_original: bool = typer.Option(
            False,
            help="Leave original files untouched, copy then rename."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="The extension of files to process."
        )
):
    Rename(initials, directory, output_directory, keep_original, extension).rename()


@app.command(help="Generates text EXIF files for photos.")
def texif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of TEXIF generation."
        ),
        type: Optional[TexifType] = typer.Option(
            TexifType.both,
            case_sensitive=False,
            help="The type of TEXIF to generate."
        ),
        level: Optional[TexifLevel] = typer.Option(
            TexifLevel.high,
            case_sensitive=False,
            help="The level of generated TEXIF data to use, only applies to simple TEXIFs."
        ),
        preset: Optional[Preset] = typer.Option(
            Preset.fujifilmxt5,
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="The extension of files to process."
        )
):
    Texif(directory, output_directory, type, level, preset, extension).texif()


@app.command(help="Generates EXIF files for photos.")
def exif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of EXIF (MIE) generation."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            help="The extension of files to process."
        )
):
    Exif(directory, output_directory, extension).exif()


def main():
    app()


if __name__ == "__main__":
    main()
