#!/usr/bin/python3

# just to be absolutely sure that confy will import its own custom utility scripts first
# It may not be necessary though, I always find python include paths to be tricky
import sys
import os
import shutil
import re

CONFY_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0,CONFY_DIR)

# built in imports

# 3rd party imports
import click


# custom utility script imports
# custom utilities will be in <confy dir>/lib
# importing will look like `from lib.<something> import <some symbols>` or `import lib.<something> as <alias>`
from lib.system import (ensure_superuser,
                        clear_all_simple_files,
                        run_ln_s,
                        run_chown_R,
                        run_chmod_R,
                        Runner,
                        file_get_contents,
                        file_put_contents
                        )

from preprocessing.handlers import le_cert

def run_preprocess_command(command_name, args):

    handler = {
        "le-cert":le_cert
    }.get(command_name,None)

    if handler is None:
        raise Exception(f"Unrecognized preprocessor command name \"{command_name}\"")

    return handler(*args)

def preprocess(contents):
    pattern = re.compile(r'^(\s*)#!\s+.*?\s*$', re.MULTILINE)

    def command_callback(match):
        leading_whitespace = match.group(1)
        # Extract command and arguments
        full_command = match.group(0).strip()
        # Assuming command is the first word after `#!`
        parts = full_command[2:].strip().split()
        command_name = parts[0]
        args = parts[1:]

        # Run the command through the router
        text =  run_preprocess_command(command_name, args).strip()

        lines = [leading_whitespace + line for line in text.splitlines()]

        return "\n".join(lines)+"\n"

    # Replace all matching lines with their processed counterparts
    processed_contents = re.sub(pattern, command_callback, contents)
    return processed_contents

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

    sites = list(filter(lambda f: f.endswith(".conf"),os.listdir(os.getcwd())))

    print("Found Sites:")
    for site in sites:
        print(f"    {site}")

    clear_all_simple_files("/etc/nginx/sites-available")
    clear_all_simple_files("/etc/nginx/sites-enabled")

    for site in sites:
        contents = file_get_contents(os.path.join(os.getcwd(),site))
        processed = preprocess(contents)
        target_file = os.path.join("/etc/nginx/sites-available",site)
        file_put_contents(target_file, processed)
        run_ln_s(
            os.path.join("/etc/nginx/sites-available",site),
            os.path.join("/etc/nginx/sites-enabled",site)
        )

    run_chown_R("/etc/nginx/sites-available","www-data:www-data")
    run_chown_R("/etc/nginx/sites-enabled","www-data:www-data")
    run_chmod_R("/etc/nginx/sites-available","755")
    run_chmod_R("/etc/nginx/sites-enabled","755")

    os.makedirs("/etc/nginx/confy",exist_ok=True)


    if os.path.isdir(os.path.join(os.getcwd(),"res")):
        if os.path.isdir("/etc/nginx/confy/res"):
            shutil.rmtree("/etc/nginx/confy/res")
        shutil.copytree(os.path.join(os.getcwd(),"res"),"/etc/nginx/confy/res")


    run_chown_R("/etc/nginx/confy/res","root:root")
    run_chmod_R("/etc/nginx/confy/res","444")

    Runner("sudo").run(["systemctl", "restart", "nginx"])


if __name__ == "__main__":
    cli()

