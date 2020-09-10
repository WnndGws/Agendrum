#!/usr/bin/env python
'''Outputs daily events from google calendar
'''

import datetime
import os
import sys

from apiclient import discovery
import httplib2
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Next set up the Google calendar scopes and files for the authentication flow
FLAGS = None
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"

if "XDG_CONFIG_HOME" in os.environ:
    BASE_DIR = os.path.expandvars('$XDG_CONFIG_HOME')
    XDG_DIR = os.path.join(BASE_DIR, "agendrum")
    if not os.path.exists(XDG_DIR):
        os.makedirs(XDG_DIR)
    CLIENT_SECRET_FILE = os.path.join(XDG_DIR, "agendrum_secrets.json")
    #Quit if file doesnt exist since Agendrum doesnt work without it
    if not os.path.isfile(CLIENT_SECRET_FILE):
        print(f'Please create "{CLIENT_SECRET_FILE}" and run Agendrum again.\
              (see https://stackoverflow.com/a/55416898 for help on how to do this)')
        sys.exit()
    CREDENTIAL_FILE = os.path.join(XDG_DIR, "agendrum_credentials.json")
else:
    BASE_DIR = os.path.expanduser("~")
    CLIENT_SECRET_FILE = os.path.join(BASE_DIR, ".agendrum_secrets")
    #Quit if file doesnt exist since Agendrum doesnt work without it
    if not os.path.isfile(CLIENT_SECRET_FILE):
        print(f'Please create "{CLIENT_SECRET_FILE}" and run Agendrum again.\
              (see https://stackoverflow.com/a/55416898 for help on how to do this)')
        sys.exit()
    CREDENTIAL_FILE = os.path.join(BASE_DIR, ".agendrum_credentials")
APPLICATION_NAME = "Agendrum"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    store = Storage(CREDENTIAL_FILE)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, FLAGS)
        print("Storing credentials to " + CREDENTIAL_FILE)
    return credentials

def get_events():
    """
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http)

    now = datetime.date.today().isoformat()
    now = now + "T00:00:00Z"
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    tomorrow = tomorrow + "T00:00:00Z"
    tomorrow_plus_one = tomorrow[:-10] + "T23:59:00Z"

    all_events = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            event_result = (
                service.events()
                .list(
                    calendarId=calendar_list_entry["id"],
                    timeMin=now,
                    timeMax=tomorrow_plus_one,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = event_result.get("items", [])
            if not events:
                pass
            for event in events:
                all_events.append(event)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return all_events

def main():
    """Prints a pretty list of events
    """

    all_events = get_events()
    today = datetime.date.today().strftime("%Y/%m/%d")
    text_list_today = []
    text_list_today_allday = []
    text_list_tomorrow = []
    text_list_tomorrow_allday = []

    for event in all_events:
        try:
            start = event["start"].get("dateTime")
            try:
                # Determine the timezone and then strip it from the string
                # Need to subtract 08 from offset since I am GMT+8
                # Will fail if no TZ since -5:-3 will be '0:'
                offset = (int(start[-5:-3]) * -1) + 8
                start = f'{start[:-6]}Z'
            except ValueError:
                offset = 8
            start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=offset)
            date = datetime.datetime.strftime(start, "%H:%M")
            start = datetime.datetime.strftime(start, "%Y/%m/%d %H:%M")
            if start[:10] == today:
                text_list_today.append(f'{date} {event["summary"]}')
            else:
                text_list_tomorrow.append(f'{date} {event["summary"]}')
        except TypeError:
            start = event["start"].get("date")
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
            start = datetime.datetime.strftime(start, "%Y/%m/%d")
            end = event["end"].get("date")
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            if start[:10] == today:
                text_list_today_allday.append(f'{event["summary"]}')
            ## Google Calendar seems to only handle allday events in UTC, so need to filter out those that dont match
            elif end > (datetime.date.today() + datetime.timedelta(days=2)):
                pass
            else:
                text_list_tomorrow_allday.append(f'{event["summary"]}')

    text_list_today.sort()
    text_list_today_allday.sort()
    text_list_tomorrow.sort()
    text_list_tomorrow_allday.sort()

    if len(text_list_today) != 0:
        max_today = len(max(text_list_today, key=len))
    else:
        max_today = 0

    if len(text_list_today_allday) != 0:
        max_today_allday = len(max(text_list_today_allday, key=len))
    else:
        max_today_allday = 0

    if len(text_list_tomorrow) != 0:
        max_tomorrow = len(max(text_list_tomorrow, key=len))
    else:
        max_tomorrow = 0

    if len(text_list_tomorrow_allday) != 0:
        max_tomorrow_allday = len(max(text_list_tomorrow_allday, key=len))
    else:
        max_tomorrow_allday = 0

    max_len = max(max_today, max_today_allday, max_tomorrow, max_tomorrow_allday)

    print_text_today = [datetime.datetime.strftime(datetime.date.today(), "%A %d/%m/%Y")]
    print_text_tomorrow = [datetime.datetime.strftime(datetime.date.today()
                                                      + datetime.timedelta(days=1), "%A %d/%m/%Y")]

    for i in text_list_today_allday:
        if i not in print_text_today:
            print_text_today.append(i)
    for i in text_list_today:
        if i not in print_text_today:
            print_text_today.append(i)
    for i in text_list_tomorrow_allday:
        if i not in print_text_tomorrow:
            print_text_tomorrow.append(i)
    for i in text_list_tomorrow:
        if i not in print_text_tomorrow:
            print_text_tomorrow.append(i)

    output = "" + print_text_today[0] + "\n"
    for i in print_text_today[1:]:
        i = i + (max_len - len(i))*"."
        output = output + i + "\n"

    output = output + " \n" + print_text_tomorrow[0] + "\n"
    for i in print_text_tomorrow[1:]:
        i = i + (max_len - len(i))*"."
        output = output + i + "\n"

    return output

if __name__ == "__main__":
    out = main()
    print(out)
