# Centralizer
## Install 
at first install dependencies \
on **Ubuntu** \
`sudo apt-get install cmake python-dev libssh2-1-dev`\
on **Centos/RHEL** \
`sudo dnf install cmake platform-python-devel libssh2-devel` \
then run this to install and run
``` bash
git clone https://github.com/LeonardoTredese/centralizer.git
pip3 install -r requirements.txt
./dashboard.py
```
## Container
### Build
inside the centralizer directory run: \
`podman build . -t centralizer`
### Run
to run a non persistent container in the background run:
``` bash
podman run --rm -d -v ${PATH_TO_YOUR_CONFIG_FILES}:/root/.centralizer/config/ -p 5000:80  --security-opt label=disable centralizer
```
and to run a non persistent interactive container run:
``` bash
podman run --rm -it -v ${PATH_TO_YOUR_CONFIG_FILES}:/root/.centralizer/config/ -p 5000:80  --security-opt label=disable centralizer
```
and connect to it: http://127.0.0.1/5000
