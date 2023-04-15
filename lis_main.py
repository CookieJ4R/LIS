"""
Main file for running this LIS-System
"""
import asyncio
import os
from dotenv import load_dotenv

from core_modules.eventing.EventDistributor import EventDistributor
from core_modules.rest.PingApi import PingApi
from core_modules.rest.RestServer import RestServer
from feature_modules.hue_integration.HueApi import HueApi
from feature_modules.hue_integration.HueInteractor import HueInteractor


async def never_ending_function():
    """
    Never ending function that keeps the main thread and event loop running.
    """
    while True:
        await asyncio.sleep(10)


async def main():
    """
    Main Coroutine that gets run on the event loop.
    """
    load_dotenv("lis.env")

    event_distributor = EventDistributor()
    event_distributor.register_event_receivers([
        HueInteractor()
    ])

    rest_server = RestServer()
    rest_server.register_apis([
        PingApi(),
        HueApi(event_distributor.put_event)
    ])
    rest_server.start_server(os.getenv("SERVER_IP"), int(os.getenv("SERVER_PORT")))

    await never_ending_function()
    # never reached!


if __name__ == "__main__":
    asyncio.run(main())
