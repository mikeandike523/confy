# Confy

A tool to synchronize NGINX configuration files per-site from a user-accessible directory (likely tracked by git)

## Requirements
todo

nginx is not necessarily required to run confy, but the purpose of confy is for the management of nginx configurations

## Installation
todo



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