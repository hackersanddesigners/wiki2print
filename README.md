# H&D Wiki-to-Print Publishing Workflow

## To-do
- update nginx section and example files after final config
- update localstettings exampel file after final config
- update the common.js and commn.css files after the final config
- figure out how venv works (@hrk?)
- make config.js.example

## Introduction
This H&D's take on the wiki-to-print workflow initially developed by the people at ConstantVZW, OSP, varia and titipi.

In short, this workflow is as follows

```
Mediawiki > HTML page > Jinja Template > PagedJS > PDF
```

Essentially there are two sides of this project:
1. [Wiki](wiki): Here, an active instance of Mediawiki facilitates the co-creation and management of publications under two associated namespaces: "Publishing" for content (written in wikitext) and "PublishingCSS" for styles (written in CSS).  
2. [Preview](preview): Here, a web-interface previews publications created in the wiki in HTML translated through Jinja templates, as well as PDF, translated through PagedJS. This interface also allows a closer inspection of the publications' CSS styles.

On the server, there are some other interwoven running processes including a MariaDB database, a python script serving an API to handle requests for creating and updating files, and several python helper scripts mediating the translations of languages across interfaces, converting images to appropriate formats, and aiding in the creation of miscelleneous styles.

## Installation

### Requirements
- A server running Debian (or other similar distro) 
- PHP version 7.1+ 
- Python3 (or at least configurable in a virtual enviroment)
- Apache2 or Nginx (we are using nginx)

Make sure you have write, read and execute persmissions at the server's web-accessible directories.

Start by cloning this repository into a web-accessible directory of your liking.
```sh
git clone https://github.com/hackersanddesigners.nl/wiki2print.git /var/www/wiki2print 
# your path could be different, we chose this one, remember it for later
```

Please follow the individual installation instructions for each of the [Wiki](wiki) and the [Preview](preview) parts of this project in their respective sub-directories and return to this section for their overlaps.

### Configurations

Each of the two side of the project has it's own configuration files and respective parameters:
1. [Wiki](wiki): The main configuration file is [LocalSettings.php](wiki/LocalSettings.example.php). Secondary files are [Common.js](wiki/Common.example.js) and [Common.css](wiki/Common.example.css).
2. [Preview](preview): The only configuration file is [config.json](preview/config.json).

The above links point to example configurations that are specific to each side of the project. Below are explanations of configurations that are shared between both.
#### Namespacing

In order for the preview side of the project to know where to look for publications in the wiki side of the project and how to handle custom configurations, we choose specific *Namespaces* for the mediawiki under which all publications exist. This is explained in detail in [this part of the documentation](wiki/README.md#namespaces). It's important that this is a custom namespace and that the preview configuration and wiki configuration both use the same ones. In this project, we use the namespace `Publishing` to house all our publications' contents and an associated namespace, `PublishingCSS` to house all our publications' styles.
#### Nginx

After setting up both sides of the project, we configure nginx to handle URLs in this way:
```sh
/        =>  localhost:5522                      # web index
/wiki    =>  /var/www/wiki2print/wiki/mediawiki  # wiki interface
```
Note: You will need to refer to this configuration during the process of installing the Mediawiki to get access to the web-installer.

See [example nignx configuration](wiki2print.nginx).

It's recommended to generate an SSL certificate for this project as user-logins are part of it. We used [Certbot](https://certbot.eff.org) for this.

## Usage

Please refer to the user documentation produced here: [docs](docs).

## License

## Authors

Heerko, Karl, Anja & Juliette
building from the work of xxxxx on xxxxx, xxxxx on xxxxx, xxxxx on xxxxx, xxxxx on xxxxx and xxxxx on xxxxx.
