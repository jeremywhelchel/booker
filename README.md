# YMCA Booker

Automated reservation grabber for YMCA pools.

Do you have trouble using the YMCA app to snag a pool reservation? This tool is designed to make that process easier and more predictable. This is a python script that runs on your local computer, not on a phone or in a browser. It allows you to see upcoming events and will request a booking at _precisely_ the moment they become available.

Note that this is simply an alternative to the YMCA app. It doesn’t have any special access, and must already be running when the reservations become available 48 hours in advance. The benefit is only due to the timing and automation. Consider this a glorified alarm clock + button-pusher.

It is upon you to continue to follow all club rules and respect reservation limits. If you abuse their system, the YMCA or Virtuagym are liable to cancel your account or membership. **Use wisely.**

Finally, be diligent in sharing this program. Reservations are already a highly contested resource. You’re racing against other users for the same bookings. Fortunately for you, most users are using the slower mobile app booking method. However if many other people start to use precise scheduling methods like this, that’ll only increase your competition and make your chances of success more difficult. It's a bit of an arms race. **Share wisely, if at all.**

## Installation and Setup

The Windows and Mac Executable methods below involve downloading and running an untrusted binary, so you will be jumping through some hoops to disable your operating system's warnings. If you have concerns, the best method is to install python on your system so that you can run the python script directly.

### Windows Executable

1. Download `booker.exe` from the [Latest Release](https://github.com/acinonyxjb/booker/releases/latest) and save it to a notable location, e.g. your `Downloads` folder. Your browser may issue a warning about an untrusted file...tell it to keep the file. **Do not click on the file to run it.**
1. Open the `Command Prompt` application.
1. Navigate to where you saved your file. For example, if you saved it to the `Downloads` folder, type:
     ```bash
     cd Downloads
     ```
1. Run the program by typing:
     ```bash
     booker.exe --help
     ```

The first time you run this, it may take a minute to extract. You should eventually see a help message, indicating success

Note that you do not need to run the program by double-clicking the downloaded file. That is not necessary since this has no GUI, and in fact may only generate an "unrecognized app" warning. Fortunately there is no warning from running with the above method.

### Mac Executable

1. Download `booker_macos.zip` from the [Latest Release](https://github.com/acinonyxjb/booker/releases/latest) and save it to a notable location, e.g. your `Downloads` folder. Your browser may issue a warning about an untrusted file...tell it to keep the file.
1. Double-click on the downloaded zip file to extract a `booker` binary.
1. Open the `Terminal` application.
1. Navigate to where you saved your file. For example, if you saved it to the `Downloads` folder, type:
     ```bash
     cd Downloads
     ```
1. Run the program by typing:
     ```bash
     ./booker --help
     ```

The first time you run this, it may take a minute to extract. You should eventually see a help message, indicating success

You may also see a warning that "booker" was blocked from use because it is not from an identifier developer. To fix, go into `System Preferences -> Security & Privacy -> General`. At the bottom you will see a message `"booker" was blocked from use because it is not from an identified developer.` next to an `Allow Anyway` button. Press that. You can find more info about this at: https://support.apple.com/en-us/HT202491


### Python environment

This is the preferred method if you already have Python installed on your machine, as you won't need to trust any foreign executables. Simply install the dependencies via `pip` and ensure the script runs.

```bash
# Install dependencies
pip3 install bs4 pandas requests

# Test that the command runs successful. You should see a help message.
./booker.py --help
```

## Usage

This runs in a command line terminal...there is no graphical interface. Some technical background is assumed.
You will be copying the commands below into the terminal window, with a few edits.

**`booker.exe`** should be replaced with the name of the binary you downloaded. Keep **`booker.exe`** unchanged on Windows. Use **`./booker`** on MacOS. Use **`./booker.py`** for Python.

**[email]** and **[password]** are the login / password from the "YMCA of Greater New York" app.

**[club]** is the name of the club, and can be one of:
  - `bedford-stuyvesant-ymca`
  - `dodge-ymca`
  - `mcburney-ymca`
  - `prospect-park-ymca`
  - `south-shore-ymca`
  - `west-side-ymca`

**[command]** is the operation you would like to perform: **`upcoming`** or **`book`**. See sections below.

For example:
```bash
booker.exe [email] [password] [club] [command]
```
could become:
```bash
./booker me@gmail.com mypassword mcburney-ymca upcoming
```

### Check upcoming events
The `upcoming` command returns a list of the next bookable events for your club.

```bash
booker.exe [email] [password] [club] upcoming
```

You should see a response like this:
```bash
Namespace(name=None, club='mcburney-ymca', command='upcoming', password='mypassword', username='me@gmail.com')
YMCA Booker starting.
Visiting homepage for mcburney-ymca...
Logging in to mcburney-ymca...SUCCESS
                                              time class_name
id
1367586815-5f7d9ee9afdd59-59343164  09:00 - 09:30   Lap Swim
385012341-5fe745fe844596-45121657   09:30 - 10:00   Lap Swim
437989699-5fe746284162c6-19786510   10:00 - 10:30   Lap Swim
2126678736-5fe7464066c143-62114372  10:30 - 11:00   Lap Swim
1083908863-5fe7465878ac91-34805573  11:00 - 11:30   Lap Swim
1011798309-5fe74685e87d38-64147158  11:30 - 12:00   Lap Swim
1835032143-5fe746a255bd78-23370620  12:00 - 12:30   Lap Swim
```

### Selecting events to book

By default, the script will look at all events in the next 48 to 72 hours, but it will not be able to book anything
until you filter it using one or more of the methods below. These are specified by flags that appear at the end of
the command-line. The script will show you what events it is trying to book before waiting for the booking period.
If the events do not look correct, you can abort the program by pressing **control-C** and then try again after editing your command.

#### Next bookable events

The simplest method is to simply grab the next *N* events that will become available. This is useful if you are running the
program roughly 48 hours in advance of when you swim. For example, this will try to grab the next two slots:

```bash
booker.exe ... --next 2
```

#### By event id

If you have a specific event id (from the output of the `upcoming` command) you can specify it directly:

```bash
booker.exe ... --id "2126678736-5fe7464066c143-62114372"
```

This also accepts multiple values:

```bash
booker.exe ... --id "2126678736-5fe7464066c143-62114372" "1011798309-5fe74685e87d38-64147158"
```

#### By starting time

You can select an event by its starting time. The time format must look like "**`08:30am`**". Otherwise it won't match an event.

Note that this matches the time in the next 48-72 hours, so double-check the date you're expecting when you run this.


```bash
booker.exe ... --time "08:30am"
```

Or multiple values:

```bash
booker.exe ... --time "08:30am" "09:00am"
```

#### By class name

Some locations have multiple pool slots at the same time, either because they have two pools or two programs at the same time. You can specify events by name.

```bash
booker.exe ... --name "Large Pool Lap Swim"
```

### Book

The `book` command attempts to reserve all selected events. It will print them out before waiting to book, so make sure it's
booking the correct events before continuing (press **control-C** to abort). Also, follow club rules...for example,
only book one event if your club prohibits back-to-back booking.

To try to grab 9:00 and 9:30 morning `Lap Swim` slots at McBurney:
```bash
booker.exe [email] [password] mcburney-ymca book --class="Lap Swim" --time "09:00am" "09:30am"
```

You should see something like this:
```bash
YMCA Booker starting.
Visiting homepage for mcburney-ymca...
Logging in to mcburney-ymca...SUCCESS

Attempting to book:
                                              time class_name
id
1367586815-5f7d9ee9afdd59-59343164  09:00 - 09:30   Lap Swim
385012341-5fe745fe844596-45121657   09:30 - 10:00   Lap Swim

Starting booking:
Next event: Lap Swim @ 2021-04-03 09:00:00-04:00
Id: ... Can schedule at: 2021-04-01 09:00:00-04:00
Waiting .. until 2021-04-01 09:00:00-04:00
<script type="text/javascript">window.location = "/classes/day/2021-04-03?event_type=2&activity_id=&coach=";</script>

Next event: Lap Swim @ 2021-04-03 09:30:00-04:00
Id: ... Can schedule at: 2021-04-01 09:30:00-04:00
Waiting .. until 2021-04-01 09:30:00-04:00
<script type="text/javascript">window.location = "/classes/day/2021-04-03?event_type=2&activity_id=&coach=";</script>
```

#### Did it work?

The above result (with the `<script ...` message) generally indicates a success. The Virtuagym server does not return a clear success or failure message, and the script does not attempt to determine one at the moment. Use the normal app or website to check and manage your current bookings.

#### Keep my computer awake

If you plan to leave your computer unattended while this job runs, you need to make sure your computer doesn’t fall asleep on you. The `caffeinate` command on Mac can be helpful here. On Windows you may need to do something else.

## Development notes

### Dependencies

Requires `python3`, `pandas`, `bs4` (beautifulsoup), `requests`

### Packaging

To create a standalone binary, we use Pyinstaller:

```bash
$ pip3 install pyinstaller
$ pyinstaller booker.py --onefile --distpath .

# On Mac:
$ zip booker_macos.zip booker
```

Which will create a `booker` or `booker.exe` binary that can be executed directly.
