copyright='gunville 2025'
import argparse
import socket
import os
from datetime import datetime

from r53dns import Arec, AAAArec
from getmyip import getMyIP

version=f'setmy53dns {copyright} v2'

privmode = os.environ.get('PRIVMODE',False)


def getFQDN(default=None):
    """Return the FQDN."""
    
    fqdn = socket.gethostname()

    if not '.' in fqdn:
        return default

    return fqdn


def parse_args():
    """ process command line arguments """

    parser = argparse.ArgumentParser(
        description='Update Route53 IP record',
        epilog=version,
        allow_abbrev=False
    )

    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=version
    )

    parser.add_argument(
        '-ip', '--ip', 
        help=f'set specific IP address to use',
        default=None
    )

    my_fqdn = getFQDN()
    parser.add_argument(
        '-fqdn', '--fqdn', 
        help=f'Fully Qualified Domain Name ({my_fqdn})',
        default=my_fqdn,
        required = my_fqdn == None
    )

    parser.add_argument(
        '-q', '--query', '--query-only', 
        help='Query only - no updates are made', 
        action='store_true',
        default=False
    )

    parser.add_argument(
        '-z', '--zone', 
        help='Route53 Zone to update (optional)',
        default=None
    )

    parser.add_argument(
        '-6', 
        help='Update AAAA record (default is A record)',
        action='store_true',
        default=False
    )

    # These are hidden and can only be set in privmode
    privaction = 'store_true' if privmode else 'store_false'

    parser.add_argument(
        '--create-record', 
        help=argparse.SUPPRESS,
        action=privaction,
        default=False
    )

    parser.add_argument(
        '--delete-record', 
        help=argparse.SUPPRESS,
        action=privaction,
        default=False
    )

    args = parser.parse_args()

    args.ipv6 = vars(args)['6']
    return args



def set_my_dns():
    """ discover public IP and update Route53 resource record """

    args = parse_args()

    fqdn = args.fqdn
    zone = args.zone or args.fqdn

    if not fqdn.endswith(zone):
        # assure fqdn ends with zone
        fqdn = f'{fqdn}.{zone}'

    
    myip = args.ip if args.ip else getMyIP(ipv6=args.ipv6)

    timenow = datetime.now().strftime("%D %T")
    print(f'\n{timenow} FQDN: {fqdn} on IP address: {myip}')

    cf = AAAArec(zone) if args.ipv6 else Arec(zone)
    rectype = cf.type

    # the actual zone
    zone = cf.zonename

    cfip = cf.get(fqdn)

    if not cfip:
        print(f'The {rectype} record for "{fqdn}" does not exist in the Route53 zone "{zone}"')
    else:
        if type(cfip) is list:
            cfip = cfip[0]
        print(f'The {rectype} record for "{fqdn}" in Route53 zone "{zone}" is currently set to {cfip}')
    
    if not args.query:
        try:
            if args.delete_record:
                print(f'\nRemoving the {rectype} record for "{fqdn}" from the Route53 zone "{zone}"')
                cf.rem(fqdn)
            
            elif args.create_record:
                print(f'\nSetting an {rectype} record for "{fqdn}" to {myip} in the Route53 zone "{zone}"')
                cf.update(fqdn,myip,addok=True)

            elif cfip and cfip != myip:
                print(f'\nUpdating the {rectype} record for "{fqdn}" from {cfip} to {myip} in the Route53 zone "{zone}"')
                r = cf.update(fqdn,myip)

            elif cfip == myip:
                print(f'\nNo changes required.')

        except Exception as e:
            print(f'\n*****Error: {str(e)}\n')
            exit(1)
    else:
        print(f'\nQuery only - no changes were made.')
    
    print()
