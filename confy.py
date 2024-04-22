#!/usr/bin/python3

# just to be absolutely sure that confy will import its own custom utility scripts first
# It may not be necessary though, I always find python include paths to be tricky
import sys
import os
import shutil
import re
import warnings

CONFY_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, CONFY_DIR)

# built in imports

# 3rd party imports
import click


# custom utility script imports
# custom utilities will be in <confy dir>/lib
# importing will look like `from lib.<something> import <some symbols>` or `import lib.<something> as <alias>`
from lib.system import (
    ensure_superuser,
    clear_all_simple_files,
    run_ln_s,
    run_chown_R,
    run_chmod_R,
    Runner,
    file_get_contents,
    file_put_contents,
)

from preprocessing.handlers import handler_manifest

def run_preprocess_command(command_name, *args):

    handler = handler_manifest.get(command_name, None)

    if handler is None:
        raise Exception(f'Unrecognized preprocessor command name "{command_name}"')

    return handler(*args)


def add_indent_string(text, indent_string):
    return "\n".join([indent_string + line for line in text.splitlines()])


def preprocess(contents):
    lines = contents.splitlines()
    processed_lines = []
    in_preproc_block = False
    preproc_start_regex = re.compile(r"^(\s*)# !! confy begin ([a-zA-Z0-9_-]+)(.*?)\s*$")
    preproc_end_regex = re.compile(r"^(\s*)# !! confy end\s*$")
    preproc_single_line_regex = re.compile(r"^(\s*)# !! confy (.+) (.+)\s*$")
    inside_block_regex=re.compile(r"^(\s*)#(.*)$")
    prepoc_command_name = ""
    preproc_source_lines = []
    block_indent_string = ""
    block_start_line_index = -1
    preproc_args = []
    for line_index, line in enumerate(lines):
        if m := preproc_start_regex.match(line):
            if in_preproc_block:
                raise Exception("Nested preprocessor blocks not supported")
            indent_string = m.group(1)
            preproc_source_lines = []
            prepoc_command_name = m.group(2).strip()
            in_preproc_block = True
            block_start_line_index = line_index
            preproc_args = []
            print(m.group(3))
            if m.group(3).strip():
                preproc_args = list(map(lambda x: x.strip(),m.group(3).strip().split(" ")))
                print(preproc_args)

        elif m := preproc_end_regex.match(line):
            if not in_preproc_block:
                raise Exception("Unbalanced end of preprocessor block")
            indent_string = m.group(1)

            if indent_string != block_indent_string:
                warnings.warn(
                    f"""Start and end indentation do not match in preprocessor block starting line {
                    block_start_line_index+1
                } and ending line { line_index+1 }"""
                )

            preproc_source = "\n".join(preproc_source_lines)

            processed_lines.extend(
                (
                    add_indent_string(
                        run_preprocess_command(prepoc_command_name, preproc_source, *preproc_args),
                        block_indent_string,
                    )
                ).splitlines()
            )
            in_preproc_block = False
        elif m := preproc_single_line_regex.match(line):
            indent_string = m.group(1)
            if in_preproc_block:
                raise Exception(
                    "Cannot run single line preprocessor directive within proeprocessor block"
                )
            processed_lines.extend(
                add_indent_string(
                    run_preprocess_command(m.group(2), m.group(3), *preproc_args), indent_string
                ).splitlines()
            )
        else:
            if in_preproc_block:
                if (m:=inside_block_regex.match(line)):
                    indent_string = m.group(1)
                    if not indent_string.startswith(block_indent_string):
                        warnings.warn(f"""
Inconsistent indent on line {line_index+1}
""")
                    preproc_source_lines.append(m.group(2))
                else:
                    raise Exception(f"""
Line {line_index+1} is not an nginx comment
""")

            else:
                processed_lines.append(line)

    return "\n".join(processed_lines)


@click.group()
def cli():
    pass


@cli.command()
def sync():
    """
    Copy the files in your project to the correct places in /etc/nginx,
    set permissions, make appropriate symlinks, and restart nginx
    """

    ensure_superuser()

    sites = list(filter(lambda f: f.endswith(".conf"), os.listdir(os.getcwd())))

    print("Found Sites:")
    for site in sites:
        print(f"    {site}")

    clear_all_simple_files("/etc/nginx/sites-available")
    clear_all_simple_files("/etc/nginx/sites-enabled")

    for site in sites:
        contents = file_get_contents(os.path.join(os.getcwd(), site))
        processed = preprocess(contents)
        target_file = os.path.join("/etc/nginx/sites-available", site)
        file_put_contents(target_file, processed)
        run_ln_s(
            os.path.join("/etc/nginx/sites-available", site),
            os.path.join("/etc/nginx/sites-enabled", site),
        )

    run_chown_R("/etc/nginx/sites-available", "www-data:www-data")
    run_chown_R("/etc/nginx/sites-enabled", "www-data:www-data")
    run_chmod_R("/etc/nginx/sites-available", "755")
    run_chmod_R("/etc/nginx/sites-enabled", "755")

    os.makedirs("/etc/nginx/confy", exist_ok=True)

    if os.path.isdir(os.path.join(os.getcwd(), "res")):
        if os.path.isdir("/etc/nginx/confy/res"):
            shutil.rmtree("/etc/nginx/confy/res")
        shutil.copytree(os.path.join(os.getcwd(), "res"), "/etc/nginx/confy/res")

    run_chown_R("/etc/nginx/confy/res", "root:root")
    run_chmod_R("/etc/nginx/confy/res", "444")

    Runner("sudo").run(["systemctl", "restart", "nginx"])


if __name__ == "__main__":
    cli()
