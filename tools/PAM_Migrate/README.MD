## The Purpose of the tool:
The Tool is mostly designe to migrate a PAM configuration to another new installed  different Platform PAM.
## Example:  
Migrate a PAM running on a VMWare to a new 1000G PAM.
* step 1: Export VMWare PAM configure
* step 2: Bootup 1000G PAM, and do basic configuration.
Interface IP, Router.  
Keep below configuration same between VMWare PAM and 1000 PAM  
    * "config system global"->"private-data-encryption"
    * web-proxy
    * EMS
    * config system central-management
* step 3: Export 1000G PAM configure
* step 4: run the tool as below usage:  
python3 pam_merge.py [VMWare_Config File]  [1000G_Config File]
* step 5: A new configure file  is created as new_dst.conf. And import the new conf to 1000G
* step 6: After 1000G bootup, the below configure might need manual to check and update:
    * secret totp
    * users with 2FA

## Notes:
After migrate configuration to new intalled PAM,  password of admin of new install PAM still keep same. It is not override by migrated configureaion.
