import os
import subprocess

from util.config import Config


class ExifTool(object):
    sentinel = "{ready}\n"

    def __init__(self, executable=Config.exiftool_executable_path):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [self.executable, "-stay_open", "True", "-@", "-"],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute_with_extension(self, extension: str, *args):
        return self.execute("-ext", extension, *args)

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()

        output = ""
        fd = self.process.stdout.fileno()

        while not output.endswith(ExifTool.sentinel):
            output += os.read(fd, 4096).decode('utf-8')

        return output[:-len(ExifTool.sentinel)]
