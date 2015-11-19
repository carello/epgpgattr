# epgpgattr

Goal of this script: Allows an administrator to find VM's based on Operating System Type, change the portgroup to something new,
then report from ACI VM's attached to EPG.

Workflow:
- User kicks off <script1>
- Prompted to enter operating system type and name of portgroup that will be used to reconfigure the VMs.

DEPENDENCIES
- Requires ACIToolKit. You can find it here: https://github.com/datacenter/acitoolkit

CREDENTIALS
- Scripts use basic user/password that is embedded into the scripts for ease of testing. Recommend a more robust auth method.






