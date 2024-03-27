#!/usr/bin/python3

# just to be absolutely sure that confy will import its own custom utility scripts first
# It may not be necessary though, I always find python include paths to be tricky
import sys
import os
import subprocess
import shutil

CONFY_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0,CONFY_DIR)

# built in imports

# 3rd party imports
import click


# custom utility script imports
# custom utilities will be in <confy dir>/lib
# importing will look like `from lib.<something> import <some symbols>` or `import lib.<something> as <alias>`


@click.group()
def cli():
    pass

@cli.command()
def check_sys():
    """
    Check if the system properly supports confy features
    """
    #todo

@cli.command()
def check_project():
    """
    Checks the integrity of the project you are using confy for, including propery .gitignore
    """
    # Atodo


@cli.command()
def where_res():
    """
    Echoes the absolute path to the "/res" folder of your project, which may be useful
    Recommended to forward to "clip" or "xclip"
    """
    click.echo(os.path.join(os.path.realpath(os.getcwd()),"res"))

@cli.command()
@click.option("--remove", is_flag=True, required=False, default=False, help="unset primary project")
def make_primary():
    """
    confy can cache the path to the current project if desired
    to ensure that the same project is being consistently used for confy operations
    """


@cli.command()
def sync():
    """
    Copy the files in your project to the correct places in /etc/nginx,
    set permissions, make appropriate symlinks, and restart ngin
    """
    with open("sites.txt","r",encoding="utf-8") as fl:
        sites = list(map(lambda l: l.strip(), fl.read().strip().splitlines()))
    
    # Step 1: Clear all files and symlinks in /etc/nginx/sites-available and /etc/nginx/sites-enabled
    sites_available_dir = "/etc/nginx/sites-available"
    sites_enabled_dir = "/etc/nginx/sites-enabled"

    for file_or_link in os.listdir(sites_available_dir):
        file_path = os.path.join(sites_available_dir, file_or_link)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)

    for file_or_link in os.listdir(sites_enabled_dir):
        file_path = os.path.join(sites_enabled_dir, file_or_link)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)

    # Step 2: Copy files to sites-available
    for site in sites:
        shutil.copyfile(os.path.realpath(site), os.path.join(sites_available_dir, site))
        print(os.path.realpath(site))

    # Step 3: Create symbolic links in sites-enabled
    for site in sites:
        os.symlink(os.path.join(sites_available_dir, site), os.path.join(sites_enabled_dir, site))

    # Step 4: Set proper permissions for files and directories
    subprocess.run(["sudo", "chown", "-R", "www-data:www-data", "/etc/nginx/sites-available"])
    subprocess.run(["sudo", "chown", "-R", "www-data:www-data", "/etc/nginx/sites-enabled"])
    subprocess.run(["sudo", "chmod", "-R", "755", "/etc/nginx/sites-available"])
    subprocess.run(["sudo", "chmod", "-R", "755", "/etc/nginx/sites-enabled"])

    # Step 5: Restart Nginx to apply changes
    subprocess.run(["sudo", "systemctl", "restart", "nginx"])


if __name__ == "__main__":
    cli()

