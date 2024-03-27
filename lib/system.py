import shutil
import os
from enum import Enum
from typing import List, Optional, Union
import subprocess

from termcolor import colored

def file_get_contents(filename:str):
    with open(filename, "r", encoding="utf-8") as fl:
        return fl.read()
    
def file_put_contents(filename:str, contents:str):
    with open(filename, "w", encoding="utf-8") as fl:
        fl.write(contents)

def read_list_from_file(filename:str):
    contents = file_get_contents(filename)
    return list(filter(lambda s:len(s)>0,map(lambda s: s.strip(),contents.rstrip().splitlines())))


def to_utf8_str(text: Union[str,bytes,None]) -> Optional[str]:
    if text is None:
        return None
    if isinstance(text,str):
        return text
    return text.decode("utf-8")

class PipeMode(Enum):
    PIPE="PIPE"
    DETACHED="DETACHED"

class RunnerResult:

    def __init__(
            self,
            stdout: Union[str,bytes,None],
            stderr: Union[str,bytes, None],
            returncode: int
    ):
        self.stdout = to_utf8_str(stdout)
        self.stderr = to_utf8_str(stderr)
        self.returncode = returncode

    def ok(self):
        return self.returncode == 0
    
    def print_self_color(self,success_color=None):
        if self.stdout is not None:
            print(colored(self.stdout,success_color))
        if self.stderr is not None:
            print(colored(self.stderr,"red"))

class Runner:

    def __init__(self, executable:str):
        if os.path.sep in executable:
            self.executable = os.path.realpath(executable)
        else:
            self.executable = shutil.which(executable)

    def run(self, args: List[str], pipe_mode: Optional[PipeMode]=PipeMode.PIPE, cwd: Optional[str]=None) -> RunnerResult:
        proc = subprocess.Popen(
            [self.executable]+args,
            # For now, stdin will always function as if detached
            # stdin=subprocess.PIPE if pipe_mode == PipeMode.PIPE else None,
            stdout=subprocess.PIPE if pipe_mode == PipeMode.PIPE else None,
            stderr=subprocess.PIPE if pipe_mode == PipeMode.PIPE else None,
            cwd=cwd
        )
        stdout, stderr = proc.communicate()

        return RunnerResult(
            stdout,
            stderr,
            proc.returncode
        )
    
def is_superuser():
    return os.geteuid() == 0

def ensure_superuser():
    if not is_superuser():
        print(colored("Superuser priveleges are required", "red"))
        exit(1)

class FileNotSimpleError(Exception):

    def __init__(self, filepath):
        super().__init__(f"File \"{filepath}\" was not a file, directory, or symlink.")
        self.filepath = filepath

def clear_all_simple_files(directory_path):
    """
    Removes all files, directories, and folders from a given folder
    Does not remove or delete the target of symlinks
    Errors if it encounters unusual/less-common file types such as pipes or sockets
    """
    for file in os.listdir(directory_path):
        fullpath = os.path.join(directory_path,file)
        if os.path.isfile(fullpath):
            os.remove(fullpath)
        elif os.path.islink(fullpath):
            os.unlink(fullpath)
        elif os.path.isdir(fullpath):
            shutil.rmtree(fullpath)
        else:
            raise FileNotSimpleError(fullpath)
        
def run_chmod_R(filename:str, permission_string:str):
    return Runner("sudo").run(["chmod","-R", permission_string, filename])

def run_chown_R(filename: str, ownership_string:str):
    return Runner("sudo").run(["chown","-R", ownership_string, filename])

def run_ln_s(from_file: str, to_file: str):
    """
    Symbolically link a regular file to a destination.
    Both the "from" and "to" must be provided as absolute paths.
    If the directories leading up to the "to" file do not exist, they will be created.
    If the "to" file is an existing symlink, it will be replaced.
    If the "to" file exists and is not a symlink, an exception is raised.
    """
    if not os.path.isfile(from_file):
        raise Exception(f"File {from_file} does not exist or is not a regular file")
    if os.path.islink(to_file):
        os.unlink(to_file)
    if not os.path.exists(os.path.dirname(to_file)):
        os.makedirs(os.path.dirname(to_file), exist_ok=True)
    elif not os.path.isdir(os.path.dirname(to_file)):
        raise NotADirectoryError(os.path.dirname(to_file))

    # No need to use os.path.basename(to_file) as we want to link directly to to_file
    return Runner("ln").run(["-s", os.path.realpath(from_file), to_file])