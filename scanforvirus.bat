@ECHO OFF
git pull

REM Comment out the next line when behind a firewall with no internet connection
clamav\freshclam.exe --config-file=config\freshclam.conf

ECHO STARTING SERVICE

start clamav\clamd.exe --config-file=config\clamd.conf --pid=clamd.pid --debug

ECHO STARTING PYTHON SCRIPT
python-venv\Scripts\python scanforvirus.py --taskbridgeurl http://192.168.0.152:42000/ --clamdip 127.0.0.1 --clamdport 3310 --worker SENECA-CPU

set /p CLAMDPID=< clamd.pid
ECHO STOPPING SERVICE %CLAMDPID%

taskkill /F /PID %CLAMDPID%

ECHO FERTIG

REM start clamav\clamd.exe