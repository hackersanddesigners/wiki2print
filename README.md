# H&D Wiki-to-Print Publishing Workflow

## Introduction
This H&D's take on the wiki-to-print workflow initially developed by the people at ConstantVZW, OSP, varia and titipi.

This workflow is as follows

```
Mediawiki > HTML page > Jinja Template > PagedJS > PDF
```

Essentially there are two sides of this project:
1. [Wiki](wiki): Here, an active instance of Mediawiki facilitates the co-creation and management of publications under two associated namespaces: "Publishing" for content (written in wikitext) and "PublishingCSS" for styles (written in CSS).  
2. [Preview](preview): Here, a web-interface previews publications created in the wiki in HTML translated through Jinja templates, as well as PDF, translated through PagedJS. This interface also allows a closer inspection of the publications' CSS styles.

On the server, there are some other interwoven running processes including mediawiki's resepective MariaDB database, a python script serving an API to handle requests for creating and updating files, and several python helper scripts mediating the translations of languages across interfaces, converting images to appropriate formats, and aiding the creation of miscelleneous styles.

## Installation

### Requirements
- A server running Debian 10+ (or other similar distro) 
- PHP version 7.1+ 
- Python3 (or at least configurable in a virtual enviroment)
- Apache2 or Nginx (we are using nginx)

Please follow the individual installation instructions for each of the [Wiki](wiki) and the [Preview](preview) parts of this project in their respective sub-directories and return to this section for their overlaps.

### Configurations

#### Nginx
#### Namespacing

## Usage

## License

## Authors




#### old 
---
# Volumetric Regimes (book)

<https://possiblebodies.constantvzw.org/book/>

<https://possiblebodies.constantvzw.org/book/index.php?title=Unfolded>

`Mediawiki > Unfolded HTML page > Jinja template > CSS + Paged.js > PDF`
