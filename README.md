# taskworker-scanforvirus

Worker for taskbridge which can handle tasks of type `scanforvirus`.

## Task format

```json
{
    ...
    "type" : "scanforvirus",
    "worker" : "ROG",
    "file" : "123456789",
    ...
    "result" : {
        "detection" : "Bad virus",
        "duration" : 12,
        "repository" : "https://github.com/hilderonny/taskworker-scanforvirus",
        "version" : "1.0.0",
        "library" : "clamd-1.0.2"
    }
}
```

The `type` must be `scanforvirus`.

`worker` contains the unique name of the worker which processed the task.

The worker expects a `file` property defining the filename which contains the file to scan.

When the worker finishes the task, it sends back a `result` property. This property is an object. It contains a property `detection` with the name of the detected virus. The property can be missing if no virus was found.

## Installation on Windows

1. First install Python 3.12.
1. Download ClamAV from https://www.clamav.net/ and put it directly into the `clamav/` directory (the runnable programs must be there).
1. Make sure to define ABSOLUTE database and log paths in `config/clamd.cong`and `config/freshclam.conf`
1. Open the Port 3310 in the firewall
1. Adopt the IP and PORT in `scanforvirus.bat` to your needs
1. Create a folder `log`
1. Next run the following commands in the repository folder

```
python3.12 -m venv python-venv
python-venv\Scripts\activate
pip install clamd==1.0.2 requests==2.32.3
```

### Running

Simply run `scanforvirus.bat`


## Linux

### Installation

1. `sudo apt install clamav clamav-freshclam clamav-daemon apparmor-utils`
2. Setup configuration with `sudo dpkg-reconfigure clamav-daemon`
    - `TCP` sockets
    - Port `3310`
    - IP address `localhost`
    - Leave the rest on default

You need to setup AppArmor to enable ClamAV to access the input files, see https://superuser.com/a/1708640.
For this run

```
sudo aa-complain /usr/sbin/clamd
```

Next run the following commands in the repository folder

```
python3.12 -m venv python-venv
source python-venv/bin/activate
pip install clamd==1.0.2 requests==2.32.3
```

Adopt the shell script `scanforvirus.sh` to your needs and create SystemD config files (if you want to run the worker as Linux service).

**/etc/systemd/system/taskworker-scanforvirus.service**:

```
[Unit]
Description=Task Worker - Virus scanner

[Service]
ExecStart=/taskworker-scanforvirus/scanforvirus.sh
Restart=always
User=user
WorkingDirectory=/taskworker-scanforvirus/

[Install]
WantedBy=multi-user.target
```

Finally register and start the services.

```
chmod +x ./scanforvirus.sh
sudo systemctl daemon-reload
sudo systemctl enable taskworker-scanforvirus.service
sudo systemctl start taskworker-scanforvirus.service
```


## Literature

1. https://www.clamav.net/