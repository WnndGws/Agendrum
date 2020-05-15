#!/usr/bin/python3
'''Outputs daily events from google calendar
'''

import datetime
import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


FLAGS = None

SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
if "XDG_CONFIG_HOME" in os.environ:
    BASE_DIR = os.path.expandvars('$XDG_CONFIG_HOME')
    XDG_DIR = os.path.join(BASE_DIR, "agendrum")
    if not os.path.exists(XDG_DIR):
        os.makedirs(XDG_DIR)
    CLIENT_SECRET_FILE = os.path.join(XDG_DIR, "agendrum_secrets.json")
    CREDENTIAL_FILE = os.path.join(XDG_DIR, "agendrum_credentials.json")
else:
    BASE_DIR = os.path.expanduser("~")
    CLIENT_SECRET_FILE = os.path.join(BASE_DIR, ".agendrum_secrets")
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
    tomorrowPlusOne = tomorrow[:-10] + "T23:59:00Z"

    allEvents = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            eventResult = (
                service.events()
               .list(
                   calendarId=calendar_list_entry["id"],
                   timeMin=now,
                   timeMax=tomorrowPlusOne,
                   singleEvents=True,
                   orderBy="startTime",
               )
               .execute()
            )
            events = eventResult.get("items", [])
            if not events:
                pass
            for event in events:
                allEvents.append(event)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break


    return allEvents

def main():
    """Prints a pretty list of events
    """

    allEvents = get_events()
    today = datetime.date.today().strftime("%Y/%m/%d")
    textListToday = []
    textListTodayAllDay = []
    textListTomorrow = []
    textListTomorrowAllDay = []
    textBox = ""

    for event in allEvents:
        try:
            start = event["start"].get("dateTime")
            try:
                start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S+08:00")
            except:
                start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=8)
            date = datetime.datetime.strftime(start, "%H:%M")
            start = datetime.datetime.strftime(start, "%Y/%m/%d %H:%M")
            if start[:10] == today:
                textListToday.append(f'{date} {event["summary"]}')
            else:
                textListTomorrow.append(f'{date} {event["summary"]}')
        except:
            start = event["start"].get("date")
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
            start = datetime.datetime.strftime(start, "%Y/%m/%d")
            end = event["end"].get("date")
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            if start[:10] == today:
                textListTodayAllDay.append(f'{event["summary"]}')
            ## Google Calendar seems to only handle allday events in UTC, so need to filter out those that dont match
            elif end > (datetime.date.today() + datetime.timedelta(days=2)):
                pass
            else:
                textListTomorrowAllDay.append(f'{event["summary"]}')

    textListToday.sort()
    textListTodayAllDay.sort()
    textListTomorrow.sort()
    textListTomorrowAllDay.sort()

    if len(textListToday) != 0:
        maxToday = len(max(textListToday, key=len))
    else:
        maxToday = 0

    if len(textListTodayAllDay) != 0:
        maxTodayAllDay = len(max(textListTodayAllDay, key=len))
    else:
        maxTodayAllDay = 0

    if len(textListTomorrow) != 0:
        maxTomorrow = len(max(textListTomorrow, key=len))
    else:
        maxTomorrow = 0

    if len(textListTomorrowAllDay) != 0:
        maxTomorrowAllDay = len(max(textListTomorrowAllDay, key=len))
    else:
        maxTomorrowAllDay = 0

    maxLen = max(maxToday, maxTodayAllDay, maxTomorrow, maxTomorrowAllDay)

    printTextToday = [datetime.datetime.strftime(datetime.date.today(), "%A %d/%m/%Y")]
    printTextTomorrow = [datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days=1), "%A %d/%m/%Y")]

    for i in textListTodayAllDay:
        if i not in printTextToday:
                printTextToday.append(i)
    for i in textListToday:
        if i not in printTextToday:
                printTextToday.append(i)
    for i in textListTomorrowAllDay:
        if i not in printTextTomorrow:
                printTextTomorrow.append(i)
    for i in textListTomorrow:
        if i not in printTextTomorrow:
                printTextTomorrow.append(i)

    output = "" + printTextToday[0] + "\n"
    for i in printTextToday[1:]:
        i  = i + (maxLen - len(i))*"."
        output = output + i + "\n"

    output = output + " \n" + printTextTomorrow[0] + "\n"
    for i in printTextTomorrow[1:]:
        i  = i + (maxLen - len(i))*"."
        output = output + i + "\n"

    return output

if __name__ == "__main__":
    output = main()
    print(output)
