import os
import shutil
import typer


class Util:
    @staticmethod
    def verify_directory(directory):
        if not os.path.isdir(directory):
            print(f"Directory [{directory}] does not exist!")
            raise typer.Exit(code=1)

    @staticmethod
    def create_directory_or_abort(directory):
        if not os.path.isdir(directory):
            print(f"Creating directory [{directory}] since it does not exist.")
            os.makedirs(directory)
        else:
            print(f"Directory [{directory}] already exists!")
            user_continue = typer.prompt(f"This will overwrite [{directory}]! Continue? (y/n)")
            if user_continue.lower() == "y":
                shutil.rmtree(directory)
                Util.create_directory_or_abort(directory)
            else:
                raise typer.Exit(code=1)

    # @staticmethod
    # def veri
