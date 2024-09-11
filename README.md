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







## Installation as service under Linux

```
sudo apt install -y git python3.11-env ocl-icd-libopencl1 nvidia-cuda-toolkit nvidia-utils-510-server nvidia-utils-535-server
python3.11 -m venv python-venv
source python-venv/bin/activate
pip install faster-whisper==0.9.0 nvidia_cublas_cu11==11.11.3.6 nvidia_cudnn_cu11==9.4.0.58
```

Adopt the shell script `translate.sh`to your needs and create SystemD config files (if you want tu run the worker as Linux service).

**/etc/systemd/system/taskworker-transcribe.service**:

```
[Unit]
Description=Task Worker - Audio Transcriber

[Service]
ExecStart=/taskworker-transcribe/transcribe.sh
Restart=always
User=user
WorkingDirectory=/taskworker-transcribe/

[Install]
WantedBy=multi-user.target
```

Finally register and start the services.

```
chmod +x ./transcribe.sh
sudo systemctl daemon-reload
sudo systemctl enable taskworker-transcribe.service
sudo systemctl start taskworker-transcribe.service
```

## Running

Running the program the first time, ai models with about 4 GB (depending on the used model) get downloaded automatically.

```sh
python transcribe.py --taskbridgeurl http://192.168.178.39:42000/ --device cuda --worker ROG --model large-v2
```

## Literature

1. https://github.com/SYSTRAN/faster-whisper