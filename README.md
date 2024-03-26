# Confy

A tool to synchronize nginx configuration filkes per-site from a user-accessible directory (likely tracked by git)

## Requirements
- modern debian based system such as Ubuntu 18.04^
- python3
- python3 click library (latest version should be ok)
  `python3 -m pip install click`
- bash available in /bin/bash


nginx is not necessarily required to run confy, but the purpose of confy is for the management of nginx configurations

## Installation
- clone the repository
  It is is recommended to clone this repository into a folder where you keep other portable cli-based tools
  For example
  `mkdir -p ~/software/portable`
  `cd ~/software/protable && git clone https://www.github.com/mikeandike523/confy`
- navigate to the installation directory
- `chmod +x configure` (as user, not root)
- `./configure` (as user, not root)

## Usage

*Usage prefixed by sudo indicates that superuser privelege is required*


- Create a new folder that will house your confy project
  It is recommended to use vcs like git
  Example:
  `mkdir my-confy-project && cd my-confy-project && git init`

- From INSIDE a given confy project
- `sudo confy import`
   Takes any existing configurations from the system and adds the files to the current project
   The import process will also scan for symlinks to detect which sites in "sites-available" are active via symlinks to "sites-enabled"
- `sudo confy sync`
   Syncronizes all configurations back to the nginx configuration directories and manages which sites are enabled via symlinks 

## Tips

- Never modify the default PRIMARY config for nginx. Out of the box it supports the recommended pattern of sites-available/sites-enabled
- Confy cannot repair a broken primary config
- If your primary config is broken, trying looking in the NGINX repository for a copy of the default primary config