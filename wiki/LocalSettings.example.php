<?php
# installer. If you make manual changes, please keep track in case you
# need to recreate them later.
#
# See includes/DefaultSettings.php for all configurable settings
# and their default values, but don't forget to make changes in _this_
# file, not there.
#
# Further documentation for configuration settings may be found at:
# https://www.mediawiki.org/wiki/Manual:Configuration_settings

# Protect against web entry
if ( !defined( 'MEDIAWIKI' ) ) {
  exit;
}


## Uncomment this to disable output compression
# $wgDisableOutputCompression = true;

$wgSitename = "H&D Publishing Wiki";
$wgMetaNamespace = "H_D_Publishing Wiki";

## The URL base path to the directory containing the wiki;
## defaults for all runtime URL paths are based off of this.
## For more information on customizing the URLs
## (like /w/index.php/Page_title to /wiki/Page_title) please see:
## https://www.mediawiki.org/wiki/Manual:Short_URL

$wgScriptPath = "/w";
$wgArticlePath = "/wiki/$1";
$wgUsePathInfo = true;
$wgUploadPath = "$wgScriptPath/images";
$wgScriptExtension = ".php";

$wgFileExtensions = array( 'png', 'gif', 'jpg', 'jpeg', 'doc',
  'xls', 'mpp', 'pdf', 'ppt', 'tiff', 'bmp', 'docx', 'xlsx',
  'pptx', 'ps', 'odt', 'ods', 'odp', 'odg'
);

## The protocol and server name to use in fully-qualified URLs
$wgServer = "https://makingmatters.karls.computer";

## The URL path to static resources (images, scripts, etc.)
$wgResourceBasePath = $wgScriptPath;

## The URL paths to the logo.  Make sure you change this from the default,
## or else you'll overwrite your logo when you upgrade!
$wgLogos = [ '1x' => "$wgResourceBasePath/resources/assets/wiki.png" ];

## UPO means: this is also a user preference option

$wgEnableEmail      = true;
$wgEnableUserEmail  = true; # UPO

$wgEmergencyContact = "karl@hackersanddesigners.nl";
$wgPasswordSender   = "karl@hackersanddesigners.nl";
$wgNoReplyAddress   = "karl@hackersanddesigners.nl";

$wgSMTP = [
  'host'     => 'ssl://smtp.migadu.com',       // hostname of the email server
  'IDHost'   => 'smtp.migadu.com',
  'port'     => 465,
  'auth'     => true,
  'username' => 'karl@hackersanddesigners.nl', // user of the email account
  'password' => '******************'           // # must be an actual password :)
];

$wgEnotifUserTalk      = true; # UPO
$wgEnotifWatchlist     = true; # UPO
$wgEmailAuthentication = true;
$wgEmailConfirmToEdit  = true;

## Database settings
$wgDBtype     = "mysql";
$wgDBserver   = "localhost";
$wgDBname     = "makingmatters";
$wgDBuser     = "mm-wiki";
$wgDBpassword = "***********"; # must be an actual password :)

# MySQL specific settings
$wgDBprefix = "";

# MySQL table options to use during installation or update
$wgDBTableOptions = "ENGINE=InnoDB, DEFAULT CHARSET=binary";

# Shared database table
# This has no effect unless $wgSharedDB is also set.
$wgSharedTables[] = "actor";

## Shared memory settings
$wgMainCacheType    = CACHE_NONE;
$wgMemCachedServers = [];

## To enable image uploads, make sure the 'images' directory
## is writable, then set this to true:
$wgEnableUploads = true;
$wgUseImageMagick = true;
$wgImageMagickConvertCommand = "/usr/bin/convert";


# InstantCommons allows wiki to use images from https://commons.wikimedia.org
$wgUseInstantCommons = false;

# Periodically send a pingback to https://www.mediawiki.org/ with basic data
# about this MediaWiki instance. The Wikimedia Foundation shares this data
# with MediaWiki developers to help guide future development efforts.
$wgPingback = true;

## If you use ImageMagick (or any other shell command) on a
## Linux server, this will need to be set to the name of an
## available UTF-8 locale. This should ideally be set to an English
## language locale so that the behaviour of C library functions will
## be consistent with typical installations. Use $wgLanguageCode to
## localise the wiki.
$wgShellLocale = "C.UTF-8";

# Site language code, should be one of the list in ./languages/data/Names.php
$wgLanguageCode = "en";

# Time zone
$wgLocaltimezone = "Europe/Berlin";

## Set $wgCacheDirectory to a writable directory on the web server
## to make your wiki go slightly faster. The directory should not
## be publicly accessible from the web.
#$wgCacheDirectory = "$IP/cache";

$wgSecretKey = "be2b5300c0bd6c7262bbf620b11ec1b365bcb33ede5bb2875fb5051a82fe3415";

# Changing this will log out all existing sessions.
$wgAuthenticationTokenVersion = "1";

# Site upgrade key. Must be set to a string (default provided) to turn on the
# web installer while LocalSettings.php is in place
$wgUpgradeKey = "1e0c30e32379da55";

## For attaching licensing metadata to pages, and displaying an
## appropriate copyright notice / icon. GNU Free Documentation
## License and Creative Commons licenses are supported so far.
$wgRightsPage = ""; # Set to the title of a wiki page that describes your license/copyright
$wgRightsUrl  = "https://creativecommons.org/licenses/by-sa/4.0/";
$wgRightsText = "Creative Commons Attribution-ShareAlike";
$wgRightsIcon = "$wgResourceBasePath/resources/assets/licenses/cc-by-sa.png";

# Path to the GNU diff3 utility. Used for conflict resolution.
$wgDiff3 = "/usr/bin/diff3";

# The following permissions were set based on your choice in the installer
$wgGroupPermissions['*']['createaccount'] = true;
$wgGroupPermissions['*']['edit'] = false;

# Enabled skins.
# The following skins were automatically enabled:
wfLoadSkin( 'MonoBook' );
wfLoadSkin( 'Timeless' );
wfLoadSkin( 'Vector' );

# These skins were installed
wfLoadSkin( 'MinervaNeue' );
wfLoadSkin( 'Citizen' );

## Default skin: you can change the default skin. Use the internal symbolic
## names, e.g. 'vector' or 'monobook':
$wgDefaultSkin = "citizen";

# Enabled extensions. Most of the extensions are enabled by adding
# wfLoadExtension( 'ExtensionName' );
# to LocalSettings.php. Check specific extension documentation for more details.
# The following extensions were automatically enabled:
wfLoadExtension( 'CodeEditor' );
wfLoadExtension( 'MultimediaViewer' );
wfLoadExtension( 'PageImages' );
wfLoadExtension( 'PdfHandler' );
wfLoadExtension( 'SyntaxHighlight_GeSHi' );
wfLoadExtension( 'VisualEditor' );
wfLoadExtension( 'WikiEditor' );

# End of automatically generated settings.
# Add more configuration options below.

wfLoadExtension( 'ConfirmAccount' );

$wgMakeUserPageFromBio = false;
$wgConfirmAccountRequestFormItems = [
	'UserName'        => [ 'enabled' => true ],
	'Biography'       => [ 'enabled' => false, 'minWords' => 50 ],
 	'AreasOfInterest' => [ 'enabled' => false ],
 	'CV'              => [ 'enabled' => false ],
 	'Notes'           => [ 'enabled' => true ],
 	'Links'           => [ 'enabled' => false ],
	'TermsOfService'  => [ 'enabled' => true ],
];

wfLoadExtension( 'UserMerge' );
$wgGroupPermissions['bureaucrat']['usermerge'] = true;

$wgNamespacesWithSubpages[NS_MAIN] = true;

define("NS_Publishing", 3000); 
$wgExtraNamespaces[NS_Publishing] = "Publishing";
$wgNamespacesWithSubpages[NS_Publishing] = true;
define("NS_PublishingCSS", 3001); 
$wgExtraNamespaces[NS_PublishingCSS] = "PublishingCSS";
$wgNamespacesWithSubpages[NS_PublishingCSS] = true;
$wgNamespaceContentModels[NS_PublishingCSS] = CONTENT_MODEL_CSS;

$wgVisualEditorAvailableNamespaces = [
  'Publishing' => true
];

wfLoadExtension( 'SubPageList3' );
