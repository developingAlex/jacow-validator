# Jacow Validator's Deployment

April / May 2019

## Where

The project is deployed on an 
[Amazon micro ec2 instance](https://us-west-2.console.aws.amazon.com/ec2/v2/home)
running 
[RHEL](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux)

currently on the lowest [tier](https://aws.amazon.com/ec2/instance-types/)
## Getting access

Provide your ssh key to the project developers who can then insert it into the 
authorized_keys file on the server when ssh'd in themselves

## Updating the ec2 instance 

To update the deployed instance to reflect the latest developments in the
master branch:

1. ssh into the ec2 instance
    
    `ssh ec2-user@ec2-54-187-195-5.us-west-2.compute.amazonaws.com`
    
1. `cd jacow-validator`

1. `source gitpull.sh`

This is a manual process, as given the project had a finite lifetime with an
obvious end date and subsequent wrap-up, CI/CD pipelines were never established.

### gitpull.sh

```
#sudo iptables -A PREROUTING -t nat -p tcp --dport 80 -j REDIRECT --to-ports 8080
# run this script to update this deployed instance with the latest changes from the github repo by running `source gitpull.sh`
sudo systemctl stop jacow
git pull
pipenv --rm
pipenv install --skip-lock
sudo systemctl start jacow
```

The commented out iptables command is a remnant from the beginnings when the 
server was running with the flask run command and the flask server was
listening on port 8080 but users would be trying to access it through port 80.

## Managing the gunicorn server

The gunicorn server is managed by systemd, the systemctl command is how you can
interface with it.


#### stopping the server

`sudo systemctl stop jacow`

#### starting the server

`sudo systemctl start jacow`

#### viewing the logs

`journalctl`

or just the last hours worth:

`journalctl --since "1 hour ago"`

or constantly follow it and see the latest updates live:

`journalctl -f`

### How gunicorn is set up with systemd

A file was created in `/etc/systemd/system/jacow.service` with the following 
content:

```
[Unit]
Description=The Jacow web server for verifying research papers
After=network.target

[Service]
PIDFile=/run/gunicorn/pid
User=ec2-user
WorkingDirectory=/home/ec2-user/jacow-validator
ExecStart=/usr/local/bin/pipenv run gunicorn -w 3 --pid /run/gunicorn/pid --timeout 180 wsgi:app -b 0.0.0.0:8080
Restart=always

[Install]
WantedBy=multi-user.target
``` 

And then its mode adjusted to rwxr-xr-x as suggested by online tutorials

A directory was also created (`/run/gunicorn`) with similar open permissions
to ensure services would have no trouble accessing it.

That file declares that the service should be restarted if it ever goes down
so now systemd will ensure that this happens automatically for us.

It also declares what the server run command is, the gunicorn command.

#### a note on the chosen gunicorn settings

The --timeout was set to 180 seconds (3mins) to ensure that if an 
[upload](https://stackoverflow.com/questions/43868863/server-fails-to-upload-large-files-with-gunicorn) 
of a document took longer than the default 30 seconds that the gunicorn worker 
would not be killed and replaced. 

The number of workers `-w 3` was set after stumbling into memory usage issues 
when attempting to run 20 workers and 
subsequently finding a suggestion that for gunicorn workers a 
[rule of thumb is 1 worker + 2 workers for every cpu](https://github.com/benoitc/gunicorn/issues/1250),
and we only have one virtual cpu. 

exerpt from the journalctl logs of the last time memory issues happened before
the change that dropped the number of workers down to 3:
```
May 10 15:38:53 ip-172-31-20-79.us-west-2.compute.internal kernel: Out of memory: Kill process 8470 (gunicorn) score 63 or sacrifice child
May 10 15:38:53 ip-172-31-20-79.us-west-2.compute.internal kernel: Killed process 8470 (gunicorn) total-vm:340852kB, anon-rss:63568kB, file-rss:296kB, shmem-rss:0kB
```

Hopefully this will be sufficient given that the documentation states:

> Gunicorn should only need 4-12 worker processes to handle 
> hundreds or thousands of requests per second.

## spms csv file

A cron job was set up to run every hour to automatically download the csv file 
from the [official jacow website](http://www.jacow.org/) to keep locally for 
use by this jacow tool in comparing crucial information between uploaded 
documents and the csv file.

## Issues encountered

The ec2 instance of RHEL that we have running appears to have an issue with its
yum package manager, in that yum has issues contacting its repositories.
This is unresolved at time of writing though research revealed a 
[couple](https://forums.aws.amazon.com/message.jspa?messageID=407853)
of 
[possible](https://serverfault.com/questions/691696/aws-yum-does-not-work-from-private-subnet-does-work-from-public) 
solutions.

The python3 that comes with the ec2 instance doesn't appear to have a sqlite 
module installed that should come with python3, as a result we didn't have the
ability to use an sqlite database and would get errors to the effect of
`no module called _sqlite3`
