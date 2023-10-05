from enum import Enum
import json
import os
import re
import requests
import time
import typer

def get_request_creds(device_url, user, password):
    login_payload = f"user={user}&password={password}"
    login_url = f"{device_url}/goform/login"
    response = requests.post(login_url, data=login_payload)
    if response.status_code == 200:
        cookies = response.cookies
        index_url  = f"{device_url}/index.asp"
        index_response = requests.get(index_url, cookies=cookies)
        if index_response.status_code != 200:
            print("cannot get index.asp")
            return
        pattern = r'value="([^"]+)"'
        match = re.search(pattern, index_response.text[-100:])
        if match:
            csrf_token = match.group(1)
            return (csrf_token, cookies)
        else:
            print("Cannot find csrf_token")
    else:
        print("Login failed with status code:", response.status_code)
    return (None, None)

def set_outlet(device_url, outlet, status, user, password):
    (token, cookies) = get_request_creds(device_url, user, password)
    if token is not None and cookies is not None:
        t = int(time.time()*1000)
        control_url = f"{device_url}/cgi-bin/control.cgi?target={outlet}&control={status}&time={t}&csrftoken={token}"
        control_response = requests.get(control_url, cookies=cookies)
        pattern = r'<outlet_status>([^<]+),([^<]+)</outlet_status>'
        match = re.search(pattern, control_response.text)
        if match:
            print(f"{match.group(1)}, {match.group(2)}")

def get_outlet_state(device_url, user, password):
    (token, cookies) = get_request_creds(device_url, user, password)
    if token is not None:
        control_url = f"{device_url}/xml/outlet_status.xml?csrftoken={token}"
        control_response = requests.get(control_url, cookies=cookies)
        pattern = r'<outlet_status>([^<]+),([^<]+)</outlet_status>'
        match = re.search(pattern, control_response.text)
        if match:
            print(f"{match.group(1)}, {match.group(2)}")
        else:
            print("no matched")
    return


class SWConfig:
    def __init__(self, fname="sw_config.json", profile="default"):
        self.profile = profile
        fname = f"{os.path.dirname(__file__)}/{fname}"
        self.creds_loaded = False
        try:
            with open(fname, "r") as f:
                self.creds = json.load(f)
                if profile not in self.creds:
                    print(f"unknown cred profile '{profile}'")
                    exit(-1)
                self.creds_loaded = True
        except Exception as e:
            print(e)
            print(f"Could not load creds from json {fname}. Will use environment")
        return

    def username(self):
        if self.creds_loaded is False:
            u = os.environ.get("SW_USERNAME", None)
            if u is not None:
                return u
            else:
                print("creds not available")
                exit(0)
        else:
            return self.creds[self.profile]["username"]

    def password(self):
        if self.creds_loaded is False:
            p = os.environ.get("SW_PASSWD", None)
            if p is not None:
                return p
            else:
                print("creds not available")
                exit(0)
        else:
            return self.creds[self.profile]["password"]

    def device_url(self):
        if self.creds_loaded is False:
            p = os.environ.get("SW_URL", None)
            if p is not None:
                return p
            else:
                print("creds not available")
                exit(0)
        else:
            return self.creds[self.profile]["device_url"]


class State(str, Enum):
    on = "on"
    off = "off"
    toggle = "toggle"
    power_cycle = "power_cycle"
    s_off = "0"
    s_on = "1"
    s_toggle = "2"
    s_powercycle = "3"

class Outlet(str, Enum):
    outlet_1 = "Outlet-1"
    outlet_2 = "Outlet-2"
    outlet_uis = "UIS"
    both = "both"
    o_uis = "1"
    o_1 = "1"
    o_2 = "2"
    o_both = "3"

def get_state(s):
    state_dict = {"on": "1", "off": "0", "toggle": "2", "power_cycle": "3"}
    return state_dict.get(s,s) 

def get_outlet(o):
    outlet_dict = {"UIS": "0", "both": "3", "Outlet-1": "1", "Outlet-2": "2"}
    return outlet_dict.get(o,o) 

app = typer.Typer()
@app.command("status")
def status():
    c = SWConfig()
    get_outlet_state(c.device_url(), c.username(), c.password())

@app.command("control")
def control(outlet: Outlet=typer.Option(default=None, metavar="--outlet", help="Outlet: 1=Outlet-1 2=Outlet-2 3=Both 0=UIS", prompt=True), 
            state: State=typer.Option(default="2", metavar="--state", help="0=off, 1=on 2=toggle 3=power-cycle", prompt=True)):
    c = SWConfig()
    set_outlet(c.device_url(), 
               get_outlet(outlet), get_state(state),
               c.username(), c.password())

if __name__ == '__main__':
    app()

