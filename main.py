import dataclasses
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from crontab import CronTab
from dateutil import parser
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pytz import timezone
from tzlocal import get_localzone

load_dotenv()

EVENT_KEYWORD = ["起床", "アラーム", "Alarm", "wake", "WAKE", "Wake", "きしょう", "起きる"]

# logging settings
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

# logger
logger = logging.getLogger(__name__)

# data directory
data_directory = "/app/data"
os.makedirs(data_directory, exist_ok=True)
schedule_file_path = os.path.join(data_directory, "alarm_schedule.json")


@dataclasses.dataclass
class Event:
    summary: str
    start: dict
    end: dict
    id: str


def get_service() -> build:
    """Get Google Calendar API service object."""
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    SERVICE_ACCOUNT_FILE = "credentials.json"
    SERVICE_ACCOUNT_FILE_PATH = get_file_path(SERVICE_ACCOUNT_FILE)

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE_PATH, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)
    return service


def get_events(service) -> List[Event]:
    """Get all events from Google Calendar."""
    calendar_id = os.environ.get("CALENDAR_ID")
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = [
        Event(
            summary=event["summary"],
            start=event["start"],
            end=event["end"],
            id=event["id"],
        )
        for event in events_result.get("items", [])
    ]
    return events


def get_alarm_events(events: List[Event]) -> List[Event]:
    """Get all events with `EVENT_KEYWORD` in the summary."""
    alarm_events = []
    for keyword in EVENT_KEYWORD:
        alarm_events += [event for event in events if keyword in event.summary]
    return alarm_events


def get_event_dict(events: List[Event]) -> Dict[str, Event]:
    """Get dictionary of events with event id as key."""
    event_dict = {event.id: event for event in events}
    return event_dict


def update_json_alarm_schedule(events: Dict[str, Event]) -> Optional[Dict[str, Event]]:
    """Update data/alarm_schedule.json with the alarm event and return the updated data."""
    active_events = set(id for id, event in events.items())
    try:
        with open(schedule_file_path, "r") as json_file:
            data = json.load(json_file)

        # Remove the alarm event that is not active
        for event_id in list(data.keys()):
            if event_id not in active_events:
                del data[event_id]

        # Update the alarm event or Create new alarm event
        for event_id, event in events.items():
            data[event_id] = dataclasses.asdict(event)

        with open(schedule_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        return data

    except FileNotFoundError:
        logger.info("data/alarm_schedule.json not found, creating a new one.")
        data = {
            event_id: dataclasses.asdict(event) for event_id, event in events.items()
        }
        with open(schedule_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4, default=str)
        logger.debug(data)
        return data

    except Exception as e:
        logger.error(f"Error reading data/alarm_schedule.json: {e}")
        return None


def get_file_path(file_name: str) -> str:
    """Get the absolute path of the alarm.py script."""
    current_file_path = os.path.abspath(__file__)
    script_path = os.path.join(os.path.dirname(current_file_path), file_name)
    return script_path


def get_start_datetime(event: Event) -> Tuple[datetime, str]:
    """Get the start datetime and timezone of the event."""
    date_time = event.get('start').get('dateTime')
    time_zone = event.get('start').get("timeZone")
    dt = parser.isoparse(date_time)
    return dt, time_zone


def convert_to_system_timezone(dt: datetime, calendar_tz_str: str) -> datetime:
    """Convert the datetime to the system timezone."""
    calendar_tz = timezone(calendar_tz_str)
    local_dt = dt.astimezone(calendar_tz)

    system_timezone = get_localzone()
    system_time = local_dt.astimezone(system_timezone)
    return system_time


def set_cron_job(alarm_time: datetime):
    """Set a cron job to run the alarm script at the specified time."""
    cron = CronTab(user=True)  # Create a new cron job
    script_path = get_file_path("alarm.py")
    job = cron.new(command=f"/usr/local/bin/python3 {script_path} >> /proc/1/fd/1 2>> /proc/1/fd/2")

    # `alarm_time`から時刻を設定
    job.minute.on(alarm_time.minute)
    job.hour.on(alarm_time.hour)
    job.day.on(alarm_time.day)
    job.month.on(alarm_time.month)
    job.dow.on(alarm_time.weekday())

    cron.write()  # crontabにジョブを保存


def remove_cron_jobs():
    """Remove all cron jobs that run the alarm script."""
    cron = CronTab(user=True)
    script_path = get_file_path("alarm.py")
    cron.remove_all(command=f"/usr/local/bin/python3 {script_path} >> /proc/1/fd/1 2>> /proc/1/fd/2")
    cron.write()


def set_all_cron_jobs(events: Dict[str, Event]):
    """Set all cron jobs for the alarm events."""
    for event in events.values():
        alarm_datetime, calendar_timezone = get_start_datetime(event)
        alarm_datetime_system = convert_to_system_timezone(
            alarm_datetime, calendar_timezone
        )
        set_cron_job(alarm_datetime_system)


def main():
    # Google Calendar APIからイベントを取得
    service = get_service()
    events = get_events(service)

    # イベントからアラームイベントを取得
    alarm_events = get_alarm_events(events)

    # json登録用に辞書に変換
    alarm_events_dict = get_event_dict(alarm_events)
    # jsonと比較してイベントを更新
    updated_alarm_events = update_json_alarm_schedule(alarm_events_dict)

    # アラームをcronジョブに設定
    # # 一度すべてのcronジョブを削除
    remove_cron_jobs()
    # 更新されたアラームイベントを再設定
    set_all_cron_jobs(updated_alarm_events)
    logger.info("Cron jobs set.")

if __name__ == "__main__":
    main()