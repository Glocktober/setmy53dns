copyright='gunville 2024'
import os
from socket import AF_INET6

import requests
import requests.packages.urllib3.util.connection as requests_cx

find_ipv4_url = 'http://ipv4.icanhazip.com/'
find_ipv6_url = 'http://ipv6.icanhazip.com/'

find_ipv4_url = os.environ.get('IPAPIURL', find_ipv4_url)
find_ipv6_url = os.environ.get('IPV6APIURL', find_ipv6_url)

def getMyIP(url=None,ipv6=False):
    """ Get this nods pulbic IP address """

    if ipv6:
        return _get_ip6(url=url if url else find_ipv6_url)
    else:
        return _get_ip(url=url if url else find_ipv4_url)


def _get_ip(url):
    """Return our external IP sourced from ipify.org"""

    return requests.get(url).text.strip()


def _get_ip6(url):
    """
    Force requests to use IPV6 AF 
    - this call only, probably not thread safe
    """

    orig_fam = requests_cx.allowed_gai_family

    def makeit6():
        return AF_INET6
    try:
        requests_cx.allowed_gai_family = makeit6
        return _get_ip(url)        
    except Exception as e:
        raise e
    finally:
        # leave the forest how you found it
        requests_cx.allowed_gai_family = orig_fam

