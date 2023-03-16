import typing

import typer

from commands.exif import Exif
from commands.info import Info
from commands.list import List
from commands.process import Process
from commands.rename import Rename, EditType
from commands.texif import Texif, Preset, TexifType, TexifLevel
from commands.yank import Yank

app = typer.Typer(help="Utility scripts to assist in renaming and generating metadata files for digital photos.")


@app.command(help="Renames photos, generates text EXIF, and generates EXIF files.")
def process(
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
        reprocess: bool = typer.Option(
            False,
            "--reprocess",
            "-r",
            help="Assuming the specified directory is a previous output folder, regenerates meta folder and files."
        ),
        preset: typing.Optional[Preset] = typer.Option(
            Preset.auto,
            "--preset",
            "-p",
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to process."
        )
):
    Process(directory, output_directory, keep_original, reprocess, preset, extension).process()


@app.command(help="Rename photos into a consistent format.")
def rename(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to rename."
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
        edit: typing.Optional[typing.List[EditType]] = typer.Option(
            [],
            "--edit",
            "-e",
            case_sensitive=False,
            help="Edit specific file name chunks instead of full rename."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to rename."
        )
):
    Rename(directory, output_directory, keep_original, edit, extension).rename()


@app.command(help="Generates text EXIF files for photos.")
def texif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to generate TEXIFs for."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of TEXIF generation."
        ),
        type: typing.Optional[TexifType] = typer.Option(
            TexifType.both,
            "--type",
            "-t",
            case_sensitive=False,
            help="The type of TEXIF to generate."
        ),
        level: typing.Optional[TexifLevel] = typer.Option(
            TexifLevel.high,
            "--level",
            "-l",
            case_sensitive=False,
            help="The level of generated TEXIF data to use, only applies to simple TEXIFs."
        ),
        preset: typing.Optional[Preset] = typer.Option(
            Preset.auto,
            "--preset",
            "-p",
            case_sensitive=False,
            help="The TEXIF file format preset to use."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to generate TEXIFs for."
        )
):
    Texif(directory, output_directory, type, level, preset, extension).texif()


@app.command(help="Generates EXIF files for photos.")
def exif(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to generate EXIFs for."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of EXIF (MIE) generation."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to generate EXIFs for."
        )
):
    Exif(directory, output_directory, extension).exif()


@app.command(help="Decodes and displays information of renamed files.")
def info(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to list information for."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to list information for."
        )
):
    Info(directory, extension).info()


@app.command(help="Moves or copies files to a different location.")
def yank(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to yank."
        ),
        output_directory: str = typer.Argument(
            "output",
            help="The directory to output the results of the yank."
        ),
        keep_original: bool = typer.Option(
            False,
            "--keep-original",
            "--keep",
            "-k",
            help="Leave original files untouched, copy only."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to yank."
        )
):
    Yank(directory, output_directory, keep_original, extension).yank()


@app.command(help="Lists files in the specified directory.")
def list(
        directory: str = typer.Argument(
            "./",
            help="The directory containing photos to list."
        ),
        output_directory: str = typer.Option(
            None,
            "--output-directory",
            "--output",
            "-o",
            help="The directory to output a text file containing the list of photos."
        ),
        full_path: bool = typer.Option(
            False,
            "--full-path",
            "--full",
            "-f",
            help="List with the full path from the current working directory."
        ),
        extension: typing.Optional[str] = typer.Option(
            "JPG",
            "--extension",
            "--ext",
            "-x",
            help="The extension of files to list."
        )
):
    List(directory, output_directory, full_path, extension).list()


def main():
    app()


if __name__ == "__main__":
    main()
