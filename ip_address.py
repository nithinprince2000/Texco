import requests
request = requests.Session();
import ipaddress
import random
import numpy as np

ipRanges = [
	"61.2.38.0/24",
	"27.251.247.0/24",
	"61.2.36.0/24",
	"27.251.119.0/24",
	"61.0.122.0/24",
	"59.93.163.0/24",
	"59.93.165.0/24",
	"59.163.108.0/24",
	"27.5.231.0/24",
	"52.172.17.0/24",
	"27.62.114.0/24",
	"59.160.147.0/24",
	"52.172.24.0/24",
	"49.204.128.0/24",
	"49.205.36.0/24",
	"61.3.253.0/24",
	"59.92.90.0/24",
	"61.3.198.0/24",
	"14.139.162.0/24",
	"61.3.192.0/24",
	"59.96.228.0/24",
	"13.71.64.0/24",
	"59.93.45.0/24",
	"61.0.125.0/24",
	"59.89.197.0/24",
	"59.96.227.0/24",
	"59.89.206.0/24",
	"61.3.122.0/24",
	"59.96.227.0/24",
	"59.89.197.0/24",
	"61.2.116.0/24",
	"59.93.46.0/24",
	"61.3.253.0/24",
	"27.62.142.0/24",
	"42.111.141.0/24",
	"61.3.196.0/24",
	"61.3.255.0/24",
	"61.1.146.0/24",
	"27.62.105.0/24",
	"61.2.139.0/24",
	"61.3.207.0/24"
]

def getIpAddress():
	np.random.shuffle(ipRanges)
	network = ipaddress.IPv4Network(random.choice(ipRanges))

	netmask = network.netmask.packed
	address = network.network_address.packed

	picked = b''
	for netmask_byte, address_byte in zip(netmask, address):
		picked += bytes([((255 ^ netmask_byte) & random.randint(0, 255)) | address_byte])

	picked = ipaddress.IPv4Address(picked)
	data = request.get("http://api.ipapi.com/api/{}?access_key=b284a0d5ddc13783dbceddcf549128eb".format(str(picked))).json()
	# print(picked)
	return "{}-{}".format(data["ip"], data["city"])