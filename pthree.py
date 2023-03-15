from typing import Optional

import typer

from commands.exif import Exif
from commands.info import Info
from commands.process import Process
from commands.rename import Rename, EditType
from commands.texif import Texif, Preset, TexifType, TexifLevel

app = typer.Typer(help="Utility scripts to assist in renaming and generating metadata files for digital photos.")


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
            "--keep-original",
            "--keep",
            "-k",
            help="Leave original files untouched, copy then rename."
        ),
        preset: Optional[Preset] = typer.Option(
            Preset.auto,
            "--preset",
            "-p",
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
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
            "--keep-original",
            "--keep",
            "-k",
            help="Leave original files untouched, copy then rename."
        ),
        edit: Optional[EditType] = typer.Option(
            EditType.none,
            "--edit",
            "-e",
            case_sensitive=False,
            help="Edit specific file name chunks instead of full rename."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to process."
        )
):
    Rename(initials, directory, output_directory, keep_original, edit, extension).rename()


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
            "--type",
            "-t",
            case_sensitive=False,
            help="The type of TEXIF to generate."
        ),
        level: Optional[TexifLevel] = typer.Option(
            TexifLevel.high,
            "--level",
            "-l",
            case_sensitive=False,
            help="The level of generated TEXIF data to use, only applies to simple TEXIFs."
        ),
        preset: Optional[Preset] = typer.Option(
            Preset.auto,
            "--preset",
            "-p",
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
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
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to process."
        )
):
    Exif(directory, output_directory, extension).exif()


@app.command(help="Decodes and displays information of renamed files.")
def info(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to process."
        ),
        extension: Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to process."
        )
):
    Info(directory, extension).info()


def main():
    app()


if __name__ == "__main__":
    main()
