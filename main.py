from dotenv import load_dotenv
load_dotenv()

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import threading
import asyncio
import time
import os

from sync import sync;

class AsyncEventHandler(FileSystemEventHandler):
    FILE_TO_WATCH = "/Users/brandonwilcox/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/ThingsData-X6GOR/Things Database.thingsdatabase/main.sqlite"  # Update this path
    MIN_TIME_BETWEEN_EVENTS = 5 # seconds

    def __init__(self, event_loop):
        self.event_loop = event_loop
        self.last_handled_time = 0

        print("Things <-> Notion sync service started")

    def should_handle_event(self):
        current_time = time.time()
        if current_time - self.last_handled_time >= self.MIN_TIME_BETWEEN_EVENTS:
            self.last_handled_time = current_time
            return True
        return False


    def on_any_event(self, event):
        if event.is_directory or event.src_path != self.FILE_TO_WATCH:
            return None

        if self.should_handle_event():
           asyncio.run_coroutine_threadsafe(sync(), self.event_loop)

if __name__ == "__main__":
    # Get or create a new event loop
    loop = asyncio.get_event_loop()
    
    # Run the observer in a separate thread
    def start_observer():
        path_to_watch = os.path.dirname(AsyncEventHandler.FILE_TO_WATCH)
        observer = Observer()
        event_handler = AsyncEventHandler(loop)
        observer.schedule(event_handler, path_to_watch, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    
    observer_thread = threading.Thread(target=start_observer)
    observer_thread.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
