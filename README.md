# YMCA Booker

Automated reservation grabber for YMCA pools.

## Usage

See the upcoming sessions
```bash
$ booker.py me@gmail.com mypassword mcburney-ymca upcoming
```

Book the next 2 upcoming `Lap Swim` slots at McBurney
```bash
$ booker.py me@gmail.com mypassword mcburney-ymca --class="Lap Swim" book 2
```

The login / password are from the "YMCA of Greater New York" app.

Requires python3, pandas, bs4 (beautifulsoup), requests

## Installation
```bash
$ sudo apt-get install python3-pip
$ pip3 install bs4 pandas requests
```

To package a standalone binary:
```bash
$ pip3 install pyinstaller
$ pyinstaller booker.py --onefile --distpath .
```

Which will create a `booker` or `booker.exe` binary that can be executed directly.
