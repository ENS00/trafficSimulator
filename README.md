# trafficSimulator
A python project which consists of simulate traffic on a road intersection and collecting all accidents statistics
You will need some libraries before issuing `python start.py`:
To install the dependencies run the following code in a terminal window:
```
python3 -m pip install -U pip
python3 -m pip install influxdb
python3 -m pip install numpy
python3 -m pip install pygame
```

# InfluxDB instance setup
In order to save data into an influxdb instance we need to install docker.

*If on linux, make sure the docker daemon is running by using this command:

$ sudo systemctl start docker

When docker is installed we need to download an influxdb image from the docker hub using this command with terminal:

(Linux bash & Windows powershell)
$ docker pull influxdb

When docker image is installed we need to start a docker continer on port 8086 and localhost(127.0.0.1):

(Linux bash & Windows powershell)
$ docker run -h 127.0.0.1 -p 8086:8086 influxdb

When the influxdb instance is running into a docker container we can start the program using `python start.py`.
