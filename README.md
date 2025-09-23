# FortiFPAM
This repository is used for sharing customized FortiPAM settings and general infos/tips about FortiPAM.

### Table Of Contents  
[Launchers](launchers/README.md)  
[Templates](templates/README.md)  
[Password-changers](pwd-changers/README.md)   
[Guides](guides/README.md)  

### Contributing
We welcome and encourage contributions to this project! To submit a pull requrest, fork the repository and push changes to any branch of the copy, then a pull request can be made in FortiPAM's main repo.   
The configuration should be added under sections under [table of contents](#table-of-contents), and contains:
- a new folder of your config's name
- a config file in  CLI format, this can be retrieved in FPAM's CLI e.g. `conf secret launcher -> edit <launcher-name> -> show full`
- a README.md file to add additional info about the config 

Example of a vaild cusotmized setting can be seen [here](<pwd-changers/Counties - SSH Password (FortiGate)>)

A pull request should contain:  
- A screenshot of the config working on FortiPAM
- The FortiPAM version
