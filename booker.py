#!/usr/bin/env python3
"""Automated reservation grabber for YMCA pools."""

import argparse
import bs4
import cmath  # hidden dep hint for pyinstaller
import datetime
import pandas as pd  # Pandas takes ~80% of the binary size
import pytz
import re
import requests
import time
from typing import Tuple


# Clubs use different event types identifiers for their pool reservations.
# This value can be found in the url while looking at the calendar. e.g.
# https://bedford-stuyvesant-ymca.virtuagym.com/classes/week/2020-10-30?event_type=2
CLUB_TO_EVENT_TYPE = {
    'bedford-stuyvesant-ymca': 2,
    'dodge-ymca': 1204,
    'mcburney-ymca': 1,
    'prospect-park-ymca': 1201,
    'south-shore-ymca': 6,
    'west-side-ymca': 2,
}
TZ = pytz.timezone('US/Eastern')


parser = argparse.ArgumentParser(description='Automate Virtuagym reservations.')
parser.add_argument('username',
                    help='Virtuagym username')
parser.add_argument('password',
                    help='Virtuagym password')
parser.add_argument('club',
                    choices=CLUB_TO_EVENT_TYPE.keys(),
                    help='Virtuagym club')
parser.add_argument('--class', help='Filter by class name')
subparser = parser.add_subparsers(dest='command', required=True,
                    help='Operation to perform')
book = subparser.add_parser('book',
                                help='Book the next N events as they become available')
book.add_argument('n', type=int, help='Number of upcoming reservations to book')
shownext = subparser.add_parser('upcoming',
                                help='Display list of upcoming boookable events.')
args = parser.parse_args()


def WaitUtil(trigger: datetime.datetime):
    now = datetime.datetime.now(TZ)
    delta = trigger - now
    print(f'Waiting {delta} until {trigger}')
    while True:
        now = datetime.datetime.now(TZ)
        if now > trigger:
            print('hit:', now)
            break
        time.sleep(0.01)


def CreateSession() -> requests.Session:
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    return session


class LoginError(RuntimeError):
    def __str__(self):
        return """
Login unsuccessful. This is likely an incorrect username and password.
However, if you're seeing this error after having previously logged in
successfully, it may be due to throttling--you may be sending too many
requests in a short time period. Wait a few minutes and try again.
"""


def Login(session: requests.Session):
    # Hit login form to grab a handful of form inputs for CSRF checking
    print(f'Visiting homepage for {args.club}...')
    response = session.get(f'https://{args.club}.virtuagym.com/')
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    sid = soup.find('input', {'name': 'sid'})['value']
    form_token = soup.find('input', {'name': 'form_token'})['value']
    creation_time = soup.find('input', {'name': 'creation_time'})['value']

    print(f'Logging in to {args.club}...', end='')
    response = session.post(f'https://{args.club}.virtuagym.com/signin?redir',
        data={
            'login': 1,
            'redirect': '%2F',
            'has_captcha': 0,
            'username': args.username,
            'password': args.password,
            'autologin': 'on',  # Might be getting logged off too soon without this set
            'sid': sid,
            'form_token': form_token,
            'creation_time': creation_time,
        }
    )
    assert response.ok
    if 'vg-user-access-token' not in session.cookies:
        raise LoginError()
    print('SUCCESS')


def Book(session: requests.Session, event_id: str) -> requests.Response:
    start_time = datetime.datetime.now().time()
    response = session.post(
        f'https://{args.club}.virtuagym.com/classes/class/{event_id}',
        data={'action': 'reserve_class'}
    )
    assert response.ok
    print(start_time, response.content.decode())
    return response


# Classes with these names are not actually bookable, so we filter them out.
BLACKLIST_CLASSES = [
        'Lap Swim Information',
]


def ResponseToEventFrame(response: requests.Response) -> pd.DataFrame:
  assert response.ok, response
  soup = bs4.BeautifulSoup(response.content, 'html.parser')

  event_ids = []
  for div in soup.find_all('div'):
    if not div.has_attr('id'):
      continue
    id = div['id']
    # Blocks with an event have a div with an id looks like this:
    #   1501788178-5f80ae4b205978-09731606_p
    #   334912091-5f80ae4b28f500-19177625_p
    #   32101852-5f456a73b5db43-81009517
    if not re.match(r'\w{5,10}-\w{14}-\w{8}_p', id):
      continue
    id = id[:-2]
    event_ids.append(id)
  assert len(event_ids)

  events = []
  for id in event_ids:
      div = soup.find('div',{'id': id})
      event = {
          'id': id,
          # Last attribute is always like: internal-event-day-01-11-2020
          'class_name': div.find('span', {'class': 'classname'}).text.strip(),
          'date': div.attrs['class'][-1][-10:],
          'time': div.find('span', {'class': 'time'}).text.strip(),
          'instructor': div.find('span', {'class': 'instructor'}).text.strip(),
          'full': 'class_full' in div.attrs['class'],
          'joined': 'class_joined' in div.attrs['class'],
      }
      events.append(event)

  events = (
      pd.DataFrame(events)
      .set_index('id')
      .assign(date=lambda x: pd.to_datetime(x['date'], dayfirst=True))
  )
  events=events.assign(start_time=(
      pd.to_datetime(events['date'].astype(str)+' '+events['time'].str.split('-').str[0])
      .map(lambda x: TZ.localize(x))
  ))

  events = events[~events['class_name'].isin(BLACKLIST_CLASSES)]
  if getattr(args, 'class'):
      events = events[events['class_name'] == getattr(args, 'class')]

  events=events[['start_time','class_name', 'full','joined','instructor','time']]
  return events


def GetSchedule(session: requests.Session) -> pd.DataFrame:
  # This might not work correctly on week boundaries.
  # First day of week here is monday. meaning running the program on friday
  # night, won't show any upcoming events.
  week = (datetime.date.today() + datetime.timedelta(2)).isoformat()
  response = session.get(
    f'https://{args.club}.virtuagym.com/classes/week/{week}',
    params={
      'event_type': CLUB_TO_EVENT_TYPE[args.club],
      'coach': 0,
      'activity_id': 0,
      'member_id_filter': 0,
      'embedded': 0,  # removes all the side stuff
      'planner_type': 7,
      'show_personnel_schedule': 0,
      'in_app': 0,  # removes the sidebar
      'single_club': 0,
    }
  )
  assert response.ok, response
  return ResponseToEventFrame(response)


def UpcomingEvents(events: pd.DataFrame) -> pd.DataFrame:
  """Find the upcoming schedulable events."""
  now = datetime.datetime.now(TZ)
  upcoming = now + datetime.timedelta(hours=48)
  upcoming_events = events[events['start_time'] > upcoming]
  return upcoming_events


def GetNextEvent(events: pd.DataFrame) -> Tuple[str, datetime.datetime]:
  """Find the event id and scheduleable time for the next event."""
  events = UpcomingEvents(events)
  next_event = events.iloc[0]
  id = next_event.name
  next_event_schedule_at = next_event.start_time - datetime.timedelta(hours=48)
  print('Next event:', next_event.class_name, '@', next_event.start_time)
  print('Id:', id, 'Can schedule at:', next_event_schedule_at)
  return id, next_event_schedule_at


def main():
    print(args)

    print('YMCA Booker starting.')
    session = CreateSession()
    Login(session)

    if args.command == 'upcoming':
        events = GetSchedule(session).pipe(UpcomingEvents)
        print(events)
    elif args.command == 'book':
        iteration = 1
        while iteration <= args.n:
            print(f'\nNew iteration: {iteration}')
            events = GetSchedule(session)
            next_id, next_time = GetNextEvent(events)

            # Wait Til 1 min before event and initate a fresh login
            WaitUtil(next_time - datetime.timedelta(minutes=1))
            session = CreateSession()
            Login(session)

            # When reservation is available, try to book.
            WaitUtil(next_time)
            response = Book(session, next_id)
            iteration += 1

        print('Hit maximum number of iterations. Terminating')
    else:
        raise ValueError(args.command)


if __name__ == "__main__":
    main()
