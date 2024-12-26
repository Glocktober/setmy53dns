
## setmy53dns - DNS updates for Route53

The scenerio exists where a servers public (external) IP address can change over time.  This is especially true with cloud computing.  

This program can be used to update Route53 public zone records automatically when a server reboots or returns from hibernation, and can be used both in the cloud and on-prem if needed.

### Limitations
`setmy53dns` will update ***existing*** DNS records - the records must ***already exist*** in your Route53 zone. 

`setmy53dns` doesn't create or remove records.  

This is by design to prevent things from going wrong.

`setmy53dns` updates **A** and **AAAA** DNS records; other records are not supported.

## setmy53dns Command Usage and Options
After configuring `setmy53dns` is simple to use and in most instances does not require any special switchs.
```bash
 % setmy53dns 
```
This will **automatically** find your public IP address and update the dns zone record based on the *fully qualifed domain name* (fqdn) of your computer.

In a more complex configuration you can use a different name or multiple ip address.
```bash
 % setmy53dns --fqdn first.example.com
 % setmy53dns --fqdn second.example.com -ip 100.100.22.23
```
A list of all availabe options:
```
% setmy53dns --help
usage: setmy53dns [-h] [-v] [-ip IP] [-fqdn FQDN] [-q] [-z ZONE] [-6]

Update Route53 IP record

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -ip IP, --ip IP       set specific IP address to use
  -fqdn FQDN, --fqdn FQDN
                        Fully Qualified Domain Name (rkmbp.sunyocc.edu)
  -q, --query           Query only - no updates are made
  -z ZONE, --zone ZONE  Route53 Zone to update (optional)
  -6                    Update AAAA record (default is A record)

setmy53dns gunville 2025 v2
```
#### Automatic IP detection:

By default `setmyip` automatically detects the public IP address by sending an HTTP request to [ipv4.icanhazip.com](http://ipv4.icanhazip.com). This site returns the IPv4 address of the sender.

You can optionally use a different site to autodetect the public ip by setting the environment variable `IPAPIURL` to that URL:
```bash
% IPAPIURL='http://api.ipify.org'
% setmy53dns
```
When ipv6 is selected with the `-6` switch automatic detection uses the ipv6 stack.  [ipv6.icanhazip.com](http://ipv6.icanhazip.com). This can be overriden with the environment variable `IPV6APIURL`.

If your host has multiple ip addresses or uses a proxy for web requests you will need to provide the ip address to use with the `--ip IP` command line switch.

```bash
% setmy53dns --ip 100.123.4.56
% setmy53dns -6 --ip 2600:1f16:a44:1701:1be3:f8b7:aa51:410b 
```

#### Automatic Hostname Determination:

The fqdn of the host is acquired with the Python `socket.gethostname()` function. (Several solutions were tried, none worked perfect, but this one seems to work best.)

There are some limitations to hostname determination:
* Some systems are not configured to provide the fqdn (*web01.example.com*) and provide only the short hostname (*web01*). There is no elegant and simple solution that works on all platforms and configurations. 

* In some environments the hostname on the private side (e.g. web01.local) is not the same one used on the public side (web01.example.com).

* Likewise, cloud VPCs by default provide hostnames in a similar fashion (e.g. *ip-172-31-84-22.ec2.internal*)

In these cases you will be required to provide the full fqdn with the `--fqdn FQDN` switch.
```bash
% setmy53dns --fqdn web01.example.com 
```

#### Route53 Zone selection:

The Route53 zone is selected from the FQDN, but can also explicity provided with the `--zone ZONE` switch.

If the `--zone` switch is used the the zone does not match the hostname determined above, the fqdn is constructed by appending the zone.
```bash
% hostname
server1
% setmy53dns --fqdn server1.example.com        # server1.example.com
% setmy53dns --fqdn server1 --zone example.com # server1.example.com
% setmy53dns --zone eample.com                 # server1.example.com
```

The above are identical. Note that the `fqdn` does not have to be 'fully qualified' when the `--zone` switch is used.

#### IPv6 Support

Both ipv4 **A** and ipv6 **AAAA** DNS records are supported by `setmy53dns`.  To update ipv6 records the `-6` switch is used - and required.

```bash
% setmy53dns -6
```

# Installation and Configuration
`setmy53dns` is easily installed using `pip`
```bash
% pip install setmy53dns
```

#### AWS Credentials

* The AWS user or role used for `setmy53dns` must have these permissions to make updates:
    * `route53:ListHostedZones` to Route53
    * `route:53ChangeResourceRecordSets` and `route53:ListResourceRecordSets` to the zones that will be updated.
    * with IAM the smallest resource scope to assign privileges is a zone.
* For EC2 instances privileges can be granted with a role attached to an EC2 instance.
* Otherwise they are provided with an AWS credentials file containing API keys to an account that has these privileges granted. (though environment variables can be used.)

#### Configuring `setmy53dns` to Run On Reboots (optional)

The following `crontab` entry will run `setmy53dns` each time the server reboots. 
```
@reboot /usr/local/bin/setmy53dns
```
The actual path depends on where you install `setmy53dns`

#### Configuring `setmy53dns` To Run Post Hibernation (optional)
This may differ some depending on the operating system. This example here works with RedHat flavors.
* Create the following file in `/lib/systemd/system-sleep/`
* Add these contents of the file 
* Set the file to be excutable

```bash
% sudo touch /lib/systemd/system-sleep/20_cfdns
% sudo chomd +x /lib/systemd/system-sleep/20_cfdns
% cat > /lib/systemd/system-sleep/20_cfdns <<EOF
#!/usr/bin/env bash
action="$1/$2"
case "$action" in
   pre/hibernate)
   ;;
   post/hibernate)
	/usr/local/bin/setmy53dns
   ;;
esac
EOF
```
The actual path depends on where you install `setmy53dns`
