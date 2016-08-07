# epgpgattr


MAIN SCRIPT : aci-sel-os-pg.py  

#####I created this script before Cisco had micro-segmentation capabilites in ACI. I'll probably depricate this script... However, some of the content might be useful for future apps.

SCRIPT OBJECTIVES
- Allows an administrator to find VM's based on Operating System Type, change the portgroup to something new,
  then report from ACI the VM's repsective EPG.

WORKFLOW
- User kicks off aci-sel-os-pg.py
- Prompted to enter operating system type and name of portgroup that will be used to reconfigure the VMs.

DEPENDENCIES
- Requires ACIToolKit. You can find it here: https://github.com/datacenter/acitoolkit

CREDENTIALS
- Scripts use basic user/password that is embedded into the scripts for ease of testing. Recommend a more robust auth method.



####OTHER SCRIPTS
- selvmos.py    : Select operating system to get back a VM report from vCTR.
- acishowep.py  : Select EPG and get back a report from APIC of endpoints.


There is limited error checking in these scripts. 





