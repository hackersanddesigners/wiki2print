# Mediawiki 

This document will take you through most of the installation steps for Mediawiki as well as highlight some of the context-specific configurations and extra hacks that makes mediawiki work for our wiki-to-print workflow.

**Important note**: This is not the location to install mediawiki. This sub-directory is mainly empty save for some reference files. This is because it is recommended to install and configure mediawiki directly on your server, rather than including it in your development/versioning workflow.

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

## Download

Navigate to this folder in your working directory:
```sh
cd /var/www/wiki2print/
```
Download the [latest stable version of mediawiki](https://www.mediawiki.org/wiki/Download):
```sh
wget https://releases.wikimedia.org/mediawiki/1.37/mediawiki-1.37.1.tar.gz
```
Extract the  mediawiki files into the directory w 
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
