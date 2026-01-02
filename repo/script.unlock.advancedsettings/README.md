# Unlock Kodi Advanced Settings

This addon allows to unlock the power of hidden Kodi system settings and
edit them through the System menu of Kodi. 

## Background
Kodi mediacenter is highly customizable system and has tons of settings,
which can be only changed by creating [advancedsewttings.xml](https://kodi.wiki/view/Advancedsettings.xml) file in the 
**userdata** folder. Changing these parameters requires manual authoring of 
the XML, which is error-prone and not always convenient.

This plugin enables editing of **advancedsettings.xml** similar to editing
settings of any other plugin.

## Installation


1. Go to the Kodi file manager, click on "Add source".
2. The path for the source is: https://Project-Kodi.github.io/ (Give it the name "Project Kodi Repository").
3. Go to "Addons", in addons, install an addon from zip. When it asks for the location, select "Project Kodi Repository", and install repository.project.kodi-1.x.x.zip.
4. Now the repository is available in Kodi, additionally, you should turn on automatic updating: Go to “Addons”, select “User Addons”, then “Addon Repository”, select “Project Kodi Repository” and activate automatic updating.
5. Go to the Addon-Browser, select “Install from Repository”, select “Project Kodi Repository”, select “User Addons”, select “Programm-Addons”, select “Unlock Kodi Advanced Settings” and chooise “Install”. Additionallyactivate automatic updating!
   
## User manual
Editing **advancedsettings.xml** is simple - just run the plugin. If you 
already have advancedsettings.xml defined in your system, it will be loaded
accordingly.

Once you complete editing changes and save them, advancedsettings.xml will be
updated (or created if it was not present in your system) in the **userddata**
folder. Old advancedsettings.xml file will be stored with **.bak** extension
in the userdata folder. 

If a setting is reverted to its default value, it will not be written to the 
advancedsettings.xml file. Parent tags without non-default settings will be automatically
removed from the file.

## Known limitations
1. Any formatting or manual comments in advancedsettings.xml will not be 
   preserved. 
2. Some settings may be not supported. In this case it is still possible to set
   them manually by editing advancedsettings.xml file. Such settings will NOT
   be overwritten by the plugin.


## Disclaimer
This is a non-commercial community-supported addon.
This plugin was created just fo fun and has no relation to official 
Kodi software. PLease know what you are doing and use at your own risk. 
Author bears no liability for any changes made by this plugin in your 
system.

## Version
Version 1.0.4 - More languages added, added repository, added more Settings,..
Version 1.0.3 - Fork from: https://github.com/abratchik/script.unlock.advancedsettings to: https://github.com/Project-Kodi/script.unlock.advancedsettings

License: [GPL v.3](http://www.gnu.org/copyleft/gpl.html)