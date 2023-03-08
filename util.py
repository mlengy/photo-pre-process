import os
import typer


class Util:
    @staticmethod
    def verify_directory(directory):
        if not os.path.isdir(directory):
            print(f"Directory {directory} does not exist!")
            raise typer.Exit(code=1)

    @staticmethod
    def verify_or_create_directory(directory):
        if not os.path.isdir(directory):
            print(f"Creating directory {directory} since it does not exist!")
            os.makedirs(directory)
