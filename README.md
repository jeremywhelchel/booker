# YMCA Booker

Automated reservation grabber for YMCA pools.

Do you have trouble using the YMCA app to snag a pool reservation? This tool is designed to make that process easier and more predictable. This is a python script that runs on your local computer, not on a phone or in a browser. It allows you to see upcoming events and will request a booking at _precisely_ the moment they become available.

Note that this is simply an alternative to the YMCA app. It doesn’t have any special access, and must already be running when the reservations become available 48 hours in advance. The benefit is only due to the timing and automation. Consider this a glorified alarm clock + button-pusher.

It is upon you to continue to follow all club rules and respect reservation limits. If you abuse their system, the YMCA or Virtuagym are liable to cancel your account or membership. **Use wisely.**

Finally, be diligent in sharing this program. Reservations are already a highly contested resource. You’re racing against other users for the same bookings. Fortunately for you, most users are using the slower mobile app booking method. However if many other people start to use precise scheduling methods like this, that’ll only increase your competition and make your chances of success more difficult. It's a bit of an arms race. **Share wisely, if at all.**

## Installation and Setup

### Windows Executable

1. Download `booker.exe` from the [Latest release](https://github.com/acinonyxjb/booker/releases/latest) and save it to a notable location, e.g. your `Downloads` folder.
1. Open the `Command Prompt` application.
1. Navigate to where you saved your file. For example, type:
   `cd Downloads`
1. Run the program by typing:
   `booker.exe --help`
   You should see a help message.

Note that you do not need to run the program by double-clicking the downloaded file. That is not necessary since this has no GUI, and in fact may only generate an "unrecognized app" warning. Fortunately there is no warning from running with the above method.

### Mac Executable

### Python environment

This is the preferred method if you already have Python installed on your machine, as you won't need to trust any foreign executables. Simply installed the dependencies via pip and ensure the script runs.

```bash
# Install dependencies
$ pip3 install bs4 pandas requests

# Test that the command runs successful. You should see a help message.
$ ./booker.py --help
```

## Usage

This runs in a command line terminal...there is no graphical interface. Some technical background is assumed.
The login / password are from the "YMCA of Greater New York" app.

### Check upcoming events
The `upcoming` command that returns a list of the next bookable events for your club.

```bash
$ booker.py me@gmail.com mypassword mcburney-ymca upcoming
```

You should see a response like this:
```bash
Namespace(class=None, club='mcburney-ymca', command='upcoming', password='mypassword', username='me@gmail.com')
YMCA Booker starting.
Visiting homepage for mcburney-ymca...
Logging in to mcburney-ymca...SUCCESS
                                                  start_time class_name   full  joined instructor           time
id
1367586815-5f7d9ee9afdd59-59343164 2021-04-03 09:00:00-04:00   Lap Swim  False   False             09:00 - 09:30
385012341-5fe745fe844596-45121657  2021-04-03 09:30:00-04:00   Lap Swim  False   False             09:30 - 10:00
437989699-5fe746284162c6-19786510  2021-04-03 10:00:00-04:00   Lap Swim  False   False             10:00 - 10:30
2126678736-5fe7464066c143-62114372 2021-04-03 10:30:00-04:00   Lap Swim  False   False             10:30 - 11:00
1083908863-5fe7465878ac91-34805573 2021-04-03 11:00:00-04:00   Lap Swim  False   False             11:00 - 11:30
1011798309-5fe74685e87d38-64147158 2021-04-03 11:30:00-04:00   Lap Swim  False   False             11:30 - 12:00
1835032143-5fe746a255bd78-23370620 2021-04-03 12:00:00-04:00   Lap Swim  False   False             12:00 - 12:30
```

### Book next available events

The `book` command attempts to reserve the next N slots as they become available. That N is adjustable--use `1` if your club prohibits back-to-back booking. Otherwise use `2`. The command also accepts an optional class name parameter, since many clubs offer multiple classes in their pool.

To try to grab the next 2 upcoming `Lap Swim` slots at McBurney
```bash
$ booker.py me@gmail.com mypassword mcburney-ymca --class="Lap Swim" book 2
```

You should see something like this:
```bash
Namespace(club='mcburney-ymca', command='book', n=2, password='mypassword', username='me@gmail.com')
YMCA Booker starting.
Visiting homepage for mcburney-ymca...
Logging in to mcburney-ymca...SUCCESS

New iteration: 1
Next event: Lap Swim @ 2021-04-03 09:00:00-04:00
Id: ... Can schedule at: 2021-04-01 09:00:00-04:00
Waiting .. until 2021-04-01 09:00:00-04:00
<script type="text/javascript">window.location = "/classes/day/2021-04-03?event_type=2&activity_id=&coach=";</script>

New iteration: 2
Next event: Lap Swim @ 2021-04-03 09:30:00-04:00
Id: ... Can schedule at: 2021-04-01 09:30:00-04:00
Waiting .. until 2021-04-01 09:30:00-04:00
<script type="text/javascript">window.location = "/classes/day/2021-04-03?event_type=2&activity_id=&coach=";</script>
```

The above result (with the `<script ...` message) generally indicates a success. The Virtuagym server does not return a clear success or failure message, and the script does not attempt to determine one at the moment. Use the normal app or website to check and manage your current bookings.

If you plan to leave your computer unattended while this job runs, you need to make sure your computer doesn’t fall asleep on you. The `caffeinate` command on Mac can be helpful here. On Windows you may need to do something else.

## Dependencies

Requires python3, pandas, bs4 (beautifulsoup), requests

## Packaging

To create a standalone binary, we use Pyinstaller:

```bash
$ pip3 install pyinstaller
$ pyinstaller booker.py --onefile --distpath .

# On Mac:
$ zip booker_macos.zip booker
```

Which will create a `booker` or `booker.exe` binary that can be executed directly.
