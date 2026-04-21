# FortiFPAM
This repository is used for sharing customized FortiPAM settings and general info/tips about FortiPAM.

### Table Of Contents
[Launchers](launchers/README.md)  
[Templates](templates/README.md)  
[Password-changers](pwd-changers/README.md)  
[Guides](guides/README.md)  

### Contributing
We welcome and encourage contributions to this project! To submit a pull request, fork the repository and push changes to any branch of the copy, then a pull request can be made in FortiPAM's main repo.
The configuration should be added under right vendors sections(create one if needed) in [table of contents](#table-of-contents), and contains:
- a new folder of your config's name
- a config file named `config` in CLI format, this can be retrieved in FPAM's CLI, e.g., `conf secret launcher -> edit <launcher-name> -> show full`
- or/and a PDF file named `gui.pdf` to show creation steps using the GUI
- a README.md file to add additional info about the config

[table of contents](#table-of-contents) should also have a link to your config file in the format of `[config link](<vendor/config_name/config>) - by <your_name>`  
Example of a valid customized setting can be seen [here](<pwd-changers/Counties - SSH Password (FortiGate)>)

A pull request should contain:
- The FortiPAM version that your config works with