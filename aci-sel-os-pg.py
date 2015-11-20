#!usr/bin python
#
# Leveraged scripts from cpaggen - github.com/cpaggen/pyvmomi/getvnicinfo.py
# cpaggen - May 16 2015 - Proof of Concept (little to no error checks)
#  - rudimentary args parser
#  - GetHostsPortgroups() is quite slow; there is probably a better way
# This code is released under the terms of the Apache 2
# http://www.apache.org/licenses/LICENSE-2.0.html
#
# Function 'change_vm_pg' Written by Reubenur Rahman
# Github: https://github.com/rreubenur/
# This code is released under the terms of the Apache 2
# http://www.apache.org/licenses/LICENSE-2.0.html
# Example script to change the network of the Virtual Machine NIC
#
# cpuskarz - Nov. 16th, 2015
# User enters Operating System and Portgroup. App queries vctr for VM/OS,
# changes the portgroup assignment, then queries APIC for EPG associations.
# This code is released under the terms of the Apache 2
# http://www.apache.org/licenses/LICENSE-2.0.html


from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import creds
import os
from tools import tasks
from showaciep import get_aci_epg


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj


def GetVMHosts(content):
    print("Getting all ESX hosts ...")
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj


def GetVMs(content):
    print ""
    print("> Getting VM data ...")
    print ""
    print "#" * 120
    vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()
    return obj

def GetHostsPortgroups(hosts):
    print("Collecting portgroups on all hosts...")
    hostPgDict = {}
    for host in hosts:
        pgs = host.config.network.portgroup
        hostPgDict[host] = pgs
        print("\tHost {} done.".format(host.name))
    print("\tPortgroup collection complete.")
    return hostPgDict

def PrintVmInfo(vm):
    if vm.config.guestFullName == sel_os:
        col_widths = [20, 20, 24, 38, 16]
        template = ''
        for idx, width in enumerate(col_widths):
            template += '{%s:%s} ' % (idx, width)
        print("")
        print("_" * 120)
        print(template.format("ADAPTER", "MAC ADDRESS", "SWITCH", "PORT GROUP", "VM NAME"))
        fmt_string = []
        for i in range(0, len(col_widths)):
            fmt_string.append('-' * (col_widths[i] - 2))
        print(template.format(*fmt_string))
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
                      + '{:<22}'.format(vSwitch)  + '    ' + '{:<38}'.format(portGroup) + '  ' +
                      '{:<35}'.format(vm.name))
                print ""
                print "> Changing PORTGROUP... "
                change_vm_pg(vmUuid)


def menu():
    print ""
    print "Select Operating System from menu, (A, B, C...):"
    print "----------------------------------"
    print "A: Ubuntu Linux (64-bit)"
    print "B: Microsoft Windows 8 (64-bit)"
    print "C: CentOS 4/5/6/7 (64-bit)"
    print ""


def change_vm_pg(vmUuid):
    # Hardcoding VDS type.
    is_VDS = True
    try:
        vm = content.searchIndex.FindByUuid(None, vmUuid, True)
        # This code is for changing only one Interface. For multiple Interface
        # Iterate through a loop of network names.
        device_change = []
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                nicspec = vim.vm.device.VirtualDeviceSpec()
                nicspec.operation = \
                    vim.vm.device.VirtualDeviceSpec.Operation.edit
                nicspec.device = device
                nicspec.device.wakeOnLanEnabled = True

                if not is_VDS:
                    nicspec.device.backing = \
                        vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicspec.device.backing.network = \
                        get_obj(content, [vim.Network], sel_pg)
                    nicspec.device.backing.deviceName = sel_pg
                else:
                    network = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], sel_pg)
                    dvs_port_connection = vim.dvs.PortConnection()
                    dvs_port_connection.portgroupKey = network.key
                    dvs_port_connection.switchUuid = \
                        network.config.distributedVirtualSwitch.uuid
                    nicspec.device.backing = \
                        vim.vm.device.VirtualEthernetCard. \
                        DistributedVirtualPortBackingInfo()
                    nicspec.device.backing.port = dvs_port_connection
                # moving indent to right; was aligned under 'else'.
                    nicspec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    nicspec.device.connectable.connected = True
                    device_change.append(nicspec)
                    #print "DONE WITH CONNECTED SECTION"
                    break

        config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
        task = vm.ReconfigVM_Task(config_spec)
        tasks.wait_for_tasks(SI, [task])
        print ">> Changed VM: %s, to Network PORT GROUP: %s " % (vm.name, sel_pg)
        print ">>> Completed."
        print ""
        print "#" * 120


    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0




def main():
    global content, hosts, hostPgDict, sel_os, vms, SI, vmUuid, sel_pg

    # Login into vctr with hard coded creds
    host, user, password, prt = creds.vm_GetArgs()
    creds.cred()
    serviceInstance = SmartConnect(host=host, user=user, pwd=password, port=prt)
    SI = serviceInstance
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()

    os.system('cls')
    menu()
    user_selection = raw_input("Enter A, B, C etc.. (default is Microsoft Windows Server 2012 (64-bit): ")
    default_os = "Microsoft Windows 8 (64-bit)"
    if user_selection.lower() == "a":
        sel_os = "Ubuntu Linux (64-bit)"
    elif user_selection.lower() == "b":
        sel_os = "Microsoft Windows 8 (64-bit)"
    elif user_selection.lower() == "c":
        sel_os = "CentOS 4/5/6/7 (64-bit)"
    else: sel_os = default_os

    print ""
    pg_name_sel = raw_input("Enter PORT GROUP NAME (case sensitive): ")
    sel_pg = pg_name_sel

    print ""
    print '#' * 120
    print ""
    hosts = GetVMHosts(content)
    hostPgDict = GetHostsPortgroups(hosts)
    vms = GetVMs(content)
    print ""

    for vm in vms:
        PrintVmInfo(vm)

    print ""
    print ""

    epg_split = pg_name_sel.split('|')
    if len(epg_split) == 1:
        epg = epg_split[0]
    else:
        epg = epg_split[2]

    print "> PORTGROUP/EPG = " + epg


    get_aci_epg(epg)

if __name__ == "__main__":
    main()





