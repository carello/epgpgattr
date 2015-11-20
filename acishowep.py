#!/usr/bin/env python

################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
"""
cpuskarz - Nov. 18, 2015
Simple application that logs on to the APIC, allows user to enter an EPG and
displays info about attached endpoints
"""

import sys
import acitoolkit.acitoolkit as aci
import creds




def main():
    # Login to APIC, using hard coded creds.
    creds.apic_GetArgs()
    url, login, password = creds.apic_GetArgs()

    default_epg = "ISO_ZONE"

    session = aci.Session(url, login, password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)

    EPG = raw_input("Enter EPG would you like to check, default is %s: " % (default_epg))
    if EPG == "":
        EPG = default_epg
    print ""

    # Download all of the interfaces and store the data as tuples in a list
    data = []
    endpoints = aci.Endpoint.get(session)
    for ep in endpoints:
        epg = ep.get_parent()
        app_profile = epg.get_parent()
        tenant = app_profile.get_parent()
        if epg.name.lower() == EPG.lower():
            data.append((ep.mac, ep.ip, ep.if_name, ep.encap, tenant.name, app_profile.name, epg.name))



    # Display the data downloaded
    col_widths = [19, 20, 40, 18, 15, 15, 10]
    template = ''
    for idx, width in enumerate(col_widths):
        template += '{%s:%s} ' % (idx, width)
    print(template.format("MACADDRESS", "IPADDRESS", "INTERFACE",
                          "ENCAP", "TENANT", "APP PROFILE", "EPG"))
    fmt_string = []
    for i in range(0, len(col_widths)):
        fmt_string.append('-' * (col_widths[i] - 2))
    print(template.format(*fmt_string))
    for rec in data:
        print(template.format(*rec))

    print ""

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
