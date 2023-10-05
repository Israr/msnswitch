Python utility to control [MSN-Switch](https://msnswitch.com/)

Usage
-----
    python msn_sw.py --outlet <outlet>  --state <control>
    python msn_sw.py status

Where control has following values

| Value     | numeric | meaning | 
|-----------| ------- | ------- | 
|  on          |   1  | Turn ON |
|  off         |   0  | Turn OFF|
|  toggle      |   2  | Toggle  |
|  power_cycle |   3  | Power Cycle (off and then on)  |

Outlet can be 1 or 2 (representing outlet 1 or outlet 2) , 3 means both, 0 means UIS)

