#!/usr/bin/env python
#
# cpaggen - May 16 2015 - Proof of Concept (little to no error checks)
#  - rudimentary args parser
#  - GetHostsPortgroups() is quite slow; there is probably a better way
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
cpuskarz - Nov. 18, 2015
User enters OS via a menu selection. Output formats :
- OS
- Power statee
- Adapter, MAC, DVS, PG, VM Name, VLAN
'''

from pyVmomi import vim,vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import creds
import sys

def GetVMHosts(content):
    print("Getting all ESX hosts ...")
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj


def GetHostsPortgroups(hosts):
    print("Collecting portgroups on all hosts. This may take a while ...")
    hostPgDict = {}
    for host in hosts:
        pgs = host.config.network.portgroup
        hostPgDict[host] = pgs
        print("\tHost {} done.".format(host.name))
    print("\tPortgroup collection complete.")
    return hostPgDict


def GetVMs(content):
    print("Getting all VMs ...")
    vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()
    return obj

def PrintVmInfo(vm):
    if vm.config.guestFullName == sel_os:
        col_widths = [20, 20, 24, 40, 35]
        template = ''
        for idx, width in enumerate(col_widths):
            template += '{%s:%s} ' % (idx, width)
        print("")
        print("_" * 141)
        print(template.format("ADAPTER", "MAC ADDRESS", "SWITCH", "PORT GROUP", "VM NAME"))
        fmt_string = []
        for i in range(0, len(col_widths)):
            fmt_string.append('-' * (col_widths[i] - 2))
        print(template.format(*fmt_string))

        print '> OS: {:<20}'.format(vm.config.guestFullName)
        print ("")

        GetVMNics(vm)


def GetVMNics(vm):
    if vm.config.guestFullName == sel_os:
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                dev_backing = dev.backing
                if hasattr(dev_backing, 'port'):
                    portGroupKey = dev.backing.port.portgroupKey
                    dvsUuid = dev.backing.port.switchUuid
                    vmUuid = vm.summary.config.uuid
                    try:
                        dvs = content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                    except:
                        portGroup = "** Error: DVS not found **"
                        vlanId = "NA"
                        vSwitch = "NA"
                    else:
                        dvsVendor = dvs.summary.productInfo.vendor
                        pgObj = dvs.LookupDvPortGroup(portGroupKey)
                        portGroup = pgObj.config.name
                        try:
                            vlanId = str(pgObj.config.defaultPortConfig.vlan.vlanId)
                        except AttributeError:
                            vlanId = "NA(VxLAN?)"
                        vSwitch = "%s %s" % (dvs.name, dvsVendor)

                else:
                    portGroup = dev.backing.network.name
                    vmHost = vm.runtime.host
                    host_pos = hosts.index(vmHost)
                    viewHost = hosts[host_pos]
                    pgs = hostPgDict[viewHost]
                    for p in pgs:
                        if portGroup in p.key:
                            vlanId = str(p.spec.vlanId)
                            vSwitch = str(p.spec.vswitchName)
                if portGroup is None:
                    portGroup = 'NA'

                print('{:<20}'.format(dev.deviceInfo.label)  + '{:<4}'.format(dev.macAddress) + '    '
                      + '{:<22}'.format(vSwitch)  + '    ' + '{:<40}'.format(portGroup) + '  '
                      + '{:<35}'.format(vm.name))




def menu():
    print ""
    print "Select Operating System from menu:"
    print "----------------------------------"
    print "A: Ubuntu Linux (64-bit)"
    print "B: Microsoft Windows 8 (32-bit)"
    print "C: CentOS 4/5/6/7 (64-bit)"
    print ""

def main():
    global content, hosts, hostPgDict, sel_os
    # Login into vctr with hard coded creds
    host, user, password, prt = creds.vm_GetArgs()
    creds.cred()
    serviceInstance = SmartConnect(host=host, user=user, pwd=password, port=prt)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()

    # get input
    menu()
    user_selection = raw_input("Enter A, B or, (default is Microsoft Windows 8 (32-bit): ")
    default_os = "Microsoft Windows 8 (32-bit)"
    if user_selection.lower() == "a":
        sel_os = "Ubuntu Linux (64-bit)"
    elif user_selection.lower() == "b":
        sel_os = "Microsoft Windows 8 (32-bit)"
    elif user_selection.lower() == "c":
        sel_os = "CentOS 4/5/6/7 (64-bit)"
    else: sel_os = default_os

    print '#########'
    hosts = GetVMHosts(content)
    hostPgDict = GetHostsPortgroups(hosts)
    vms = GetVMs(content)
    print '#########'
    for vm in vms:
        PrintVmInfo(vm)
    print ""


if __name__ == "__main__":
    main()




