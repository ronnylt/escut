# Escut is a Distributed Lock Manager over HTTP built on [Tornado] and
backed by Redis.

## Features

- HTTP interface

## Nice to have features
- Blocking wait for acquiring a lock (with customatizable timeout)

### Installation

    Requirements: 
    - Python 2.7
    - Tornado >= 2.3
                  
### Starting the daemon

    escutd.py --port=9595 --logging=debug