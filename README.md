# RRT* SIMULATION

Simulate RRT* (Rapidly-exploring Random Tree STAR) algorithm with Python in 2 scenarios:
- Easy: no lane, only obstacles
- Hard: complex lanes and obstacles


<p float="left">
  <image src="images/wo_lines.gif" width="400" hspace="10"/>
  <image src="images/withLines.gif" width="400"/> 
</p>

## Environment 
- Python 3.7
- Ubuntu 20.04

## Requirements
Install necessary packages followed ```requirements.txt```
```
pip install -r requirements.txt
```

## How to use

### Configure properties in ```cfg.py```: 
- start node
- target node
- obstacle size
- number of obstacles
- etc., 

### Run simulation

- Easy Mode (default):
    ```
    python RRTS.py 
    ```
    or
    ```
    python RRTS.py -m easy
    ```
- Hard Mode:
    ```
    python RRTS.py -m hard
    ```
Code for the lower version (RRT) is **[here](https://github.com/tuminguyen/RRT_Simulation_Path_Planning)**