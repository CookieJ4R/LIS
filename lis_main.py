"""
Main file for running this LIS-System
"""
import asyncio

from core_modules.eventing.EventDistributor import EventDistributor
from core_modules.logging.lis_logging import get_logger
from core_modules.rest.PingApi import PingApi
from core_modules.rest.RestServer import RestServer
from core_modules.scheduling.EventScheduler import EventScheduler
from core_modules.scheduling.SchedulableEvent import EVENT_ID_DATA_FIELD
from core_modules.scheduling.SchedulingApi import SchedulingApi
from core_modules.storage.StorageManager import StorageManager, SECTION_HEADER_SERVER, FIELD_SERVER_IP, \
    FIELD_SERVER_PORT
from feature_modules.hue_integration.HueApi import HueApi
from feature_modules.hue_integration.HueInteractor import HueInteractor
from feature_modules.spotify_integration.SpotifyEvents import SpotifyStartResumePlaybackEvent, SpotifyPausePlaybackEvent
from feature_modules.spotify_integration.SpotifyInteractor import SpotifyInteractor

log = get_logger("lis_main")


async def never_ending_function():
    """
    Never ending function that keeps the main thread and event loop running.
    """
    log.info("Starting infinite async loop...")
    while True:
        await asyncio.sleep(10)


async def main():
    """
    Main Coroutine that gets run on the event loop.
    """
    storage = StorageManager("lis_data.toml")

    event_distributor = EventDistributor()

    event_scheduler = EventScheduler(storage, event_distributor.put_internal)

    event_distributor.register_event_receivers([
        event_scheduler,
        HueInteractor(storage, event_distributor.put_internal),
        SpotifyInteractor(storage)
    ])

    event_scheduler.load_persistent_events(event_distributor.map_to_schedulable_event)

    rest_server = RestServer(event_distributor.put_internal)
    rest_server.register_apis([
        PingApi(),
        HueApi(event_distributor.put_internal),
        SchedulingApi(event_distributor.put_internal, event_distributor.map_to_schedulable_event)
    ])
    rest_server.start_server(storage.get(FIELD_SERVER_IP, section=SECTION_HEADER_SERVER, fallback="127.0.0.1"),
                             storage.get(FIELD_SERVER_PORT, section=SECTION_HEADER_SERVER, fallback=5000))

    await never_ending_function()
    # never reached!


if __name__ == "__main__":
    log.info("Starting LIS...")
    asyncio.run(main())
