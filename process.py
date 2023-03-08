import typer


class Process:
    def __init__(self, directory, output_directory, level):
        self.directory = directory
        self.output_directory = output_directory
        self.level = level

    def process(self):
        pass
