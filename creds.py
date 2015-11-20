#!/usr/bin/env python


import ssl
import requests
requests.packages.urllib3.disable_warnings()

def cred():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
     pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

def vm_GetArgs():
    # enter in your credentials for your vCTR environment
    host = "x.x.x.x"
    user = "x"
    password = "x"
    prt = 443
    return host, user, password, prt

def apic_GetArgs():
    # enter in your credentials for your APIC
    url = "http://x.x.x.x"
    login = "x"
    password = "x"
    return url, login, password
