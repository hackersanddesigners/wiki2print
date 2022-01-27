# Mediawiki 

This document will take you through most of the installation steps for Mediawiki as well as highlight some of the context-specific configurations and extra hacks that makes mediawiki work for our wiki-to-print workflow.

**Important note**: This sub-directory is mainly empty save for some reference files. This is because it is recommended to install and configure mediawiki directly on your server, rather than including it in your development/versioning workflow. For instance, our `.gitignore` file looks like this:
```sh
wiki/mediawiki
```
A folder dedicated to mediawiki installation files will be created directly on the server and excluded from our git workflow.

# Installation

There are [several ways of installing mediawiki](https://www.mediawiki.org/wiki/Manual:Installation_guide#Main-installation-guide), and this is the way that worked for our environment. We followed [these steps](https://www.mediawiki.org/wiki/Manual:Installing_MediaWiki) and will highlight them here.

## Requirements
*(software and os versions are as we had them on the installation date)*
| Software     | Version |
|--------------|:-------:|
| Debian Linux |   6.3.0 |
| Mediawiki    |  1.37.1 |
| PHP          |  7.3.31 |
| MariaDB      | 10.3.31 |
| Nginx        |  1.14.2 |

Make sure you have already cloned this repository into a web-accessible folder on your remote server.

## Download

Navigate to this folder in your working directory:
```sh
cd /var/www/wiki2print/wiki
```
Download the [latest stable version of mediawiki](https://www.mediawiki.org/wiki/Download):
```sh
wget https://releases.wikimedia.org/mediawiki/1.37/mediawiki-1.37.1.tar.gz
```
Extract the  mediawiki files.
```sh
tar -xf mediawiki-*.tar.gz 
```
Change the name of the extracted folder to `mediawiki` and (optionally) delete the downloaded tarball:
```sh
mv mediawiki-1.37.1 mediawiki
rm mediawiki-*.tar.gz 
```
Your directory should look like this
```sh
ls /var/www/wiki2print/wiki
LocalSettings.example.php
README.md
mediawiki
```
Please note the nested structure here: `mediawiki` is inside our own `wiki` but is excluded from our git workflow (using our top level `.gitignore` file).

### Creating a database

[From the mediawiki installation manual](https://www.mediawiki.org/wiki/Manual:Installing_MediaWiki#Create_a_database): "If you already have a database server and know the root password for it, the MediaWiki installation script can create a new database for you... If you don't know the root password, for example if you are on a hosted server, you will have to create a new database now."

We already have a MariaDB database server installed and went ahead with the installation script. Note that this isn't the only mediawiki installed on our server, so we took care to name the databases differently.

### Web Installation

Before heading over to the Web Installation script, make sure you can access the files you just put on the server through a web-browser.

We have attached an [NGINX example configuration](/wiki2print.nginx.example) in the root of this workinng directory. Please refer to [this section](/README.md#nginx) for details on this configuration.

### User creation

### Namespaces

### Theme

### Extra buttons!
