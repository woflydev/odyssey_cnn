# install system dependencies for the project
sudo apt-get update
sudo apt-get install libhidapi-dev -y # hidapi library for controller
sudo apt-get install python3-smbus -y 
sudo apt-get install i2c-tools -y
# just update cuz why not
pip3 install -r requirements.txt