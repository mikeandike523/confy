# Confy

A tool to synchronize NGINX configuration files per-site from a user-accessible directory (likely tracked by git)

## Requirements
- modern debian based system such as Ubuntu 18.04^
- python3
- python3 click library (latest version should be ok)
  `python3 -m pip install click`
- bash available in /bin/bash

nginx is not necessarily required to run confy, but the purpose of confy is for the management of nginx configurations

## Installation
- It is recommended to install confy to a folder in your home directory dedicated to the installation of portable software
```
cd ~
mkdir -p portable
cd portable
# In case an older version of confy has already been installed
rm -rf confy
git clone https://www.github.com/mikeandike523/confy
cd confy
sudo chmod +x ./configure
sudo ./configure
```
- This will create the appropriate symlink in /usr/local/bin making the `confy` command available on the command line
- "confy" is installed as the current user, although some confy commands may require running as sudo



## Usage

*Usage prefixed by sudo indicates that superuser privelege is required*


- Create a new folder that will house your confy project
  It is recommended to use vcs like git
  Example:
  `mkdir my-confy-project && cd my-confy-project && git init`

- From INSIDE a given confy project

- `sudo confy sync`
   Syncronizes all configurations back to the nginx configuration directories and manages which sites are enabled via symlinks
   Copies "res" files to /etc/nginx/confy/res and sets permission (-R) of the folder to 444 (read only) 

## Tips

- Never modify the default PRIMARY config for nginx. Out of the box it supports the recommended pattern of sites-available/sites-enabled
- Confy cannot repair a broken primary config
- If your primary config is broken, trying looking in the NGINX repository for a copy of the default primary config