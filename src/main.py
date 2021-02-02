#!/usr/bin/env python3

import requests
import json
import subprocess


def get_config():
    with open('/app/secrets.json') as json_file:
        return json.load(json_file)


def get_current_ip():
    req = requests.get('https://api.ipify.org?format=json')
    currentIp = req.json()["ip"]
    return currentIp


def get_last_ip():
    return subprocess.run(['cat', '/app/lastIp'], stdout=subprocess.PIPE) \
                        .stdout \
                        .decode('utf-8') \
                        .strip()


def update(zone, domain):
    header = {"X-Auth-Key": authKey,
              "X-Auth-Email": email,
              "Content-Type": "application/json"}
    req = requests.get("https://api.cloudflare.com/client/v4/zones/",
                       headers=header)
    zones = req.json()
    for result in zones["result"]:
        if(result["name"] == zone):
            print("Connected to zone "+result["name"])
            req = requests.get("https://api.cloudflare.com/client/v4/zones/" +
                               result["id"]+"/dns_records?type=A",
                               headers=header)
            for dns in req.json()["result"]:
                print("Checking dns record "+dns["name"])
                if(dns["name"].startswith(domain)):
                    d = json.dumps({"type": "A",
                                    "name": dns["name"],
                                    "content": currentIp})
                    req = requests.put(
                                "https://api.cloudflare.com/client/v4/zones/" +
                                result["id"]+"/dns_records/"+dns["id"],
                                headers=header, data=d)
                    print(req.json())
                    if req.status_code == 200:
                        print("Succesfully updated DNS record")
                        with open("/app/lastIp", "w") as file:
                            file.write(currentIp)


if __name__ == '__main__':

    data = get_config()
    email = data["email"]
    authKey = data["authKey"]
    domain = data["domain"]
    zone = data["zone"]

    currentIp = get_current_ip()
    lastIp = get_last_ip()

    print("Current IPv4 = " + currentIp)
    print("Previous IPv4 = " + lastIp)

    if(currentIp == ""):
        print("No IP has been provided")
        exit()
    if(currentIp != lastIp):
        print("Ip has changed!")
        print("Updating DNS...")
        for z in zone:
            update(domain, z)
    else:
        print("Ip has not been changed")
