from asyncio.streams import StreamReader, StreamWriter
from typing import Dict, List
import asyncio
import serial_asyncio
from serial import SerialException
from asyncio import CancelledError
import logging
import sys
import datetime
import traceback
import re

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

REFRESH_INTERVAL = 3600


class DmxController:
    def __init__(self, device, baud=9600, loop=asyncio.get_event_loop()) -> None:
        self.SERIAL_PORT = device
        self.BAUD_RATE = baud

        self.loop:asyncio.AbstractEventLoop = loop
        self.reader: StreamReader = None
        self.writer: StreamWriter = None

        self._channels :Dict[int, DmxChannel]= {}


        log.debug("Initializing Main")
        loop.create_task(self.main())

    async def restart(self):
        # reset everything on errrors
        self.reader = None
        self.writer = None
        self.loop.create_task(self.main())

    def getChannel(self, c:int) -> 'DmxChannel':
        if c not in self._channels.keys():
            self._channels[c] = DmxChannel(self,c)
            self.loop.create_task(self.updateZoneLevel(c))
        return self._channels.get(int(c))

    async def updateZoneLevel(self, c:int):
            await self.sendCommand(str(c)+"cg")

    async def main(self):
        self.loop.create_task(self.listen())
        while True:
            if not self.reader or not self.writer:
                log.debug(
                    "Connecting to: {}  Baud: {}".format(
                        self.SERIAL_PORT, self.BAUD_RATE
                    )
                )
                try:
                    (
                        self.reader,
                        self.writer,
                    ) = await serial_asyncio.open_serial_connection(
                        url=self.SERIAL_PORT, baudrate=self.BAUD_RATE
                    )
                # except (SerialException, OSError, FileNotFoundError):
                except:
                    log.exception("Caught Serial Exception")
                    await asyncio.sleep(2)
                    break

                log.debug("DMX Controller Connected")
            await asyncio.sleep(60)

    async def sendCommand(self, command: str):
        message = bytes(command, "ASCII") + b"\r\n"
        self.writer.write(message)


    async def listen(self):
        while True:
            if self.reader:
                try:
                    line = await self.reader.readline()
                    line = line.decode("ASCII")
                    log.debug("DMX Received: {}".format(line))                   
                    line.rstrip("\r\n")
                    regex = r"(?P<channel>\d{1,3})c(?P<level>\d{1,3})l"
                    m = re.match(regex, line)
                    if m:
                        self.getChannel(m.group("channel")).level = m.group("level")


                except CancelledError:
                    break
                except:
                    # traceback.print_exception(*exc_info)
                    log.exception("Listen function threw exception")
                    await asyncio.sleep(.5)
            else:
                await asyncio.sleep(1)



class DmxChannel:
    def __init__(self, controller:DmxController, channelNum:int) -> None:
        self.controller = controller
        self.channelNum = int(channelNum)
        self.level = 0
        self.callBacks = []
    
    async def setLevel(self, level:int, fadeSpeed:int=0):
        level = round(level)
        fadeSpeed = round(fadeSpeed)
        command = "{}c{}f{}w".format(self.channelNum, fadeSpeed,  level)
        log.debug("Sending Command:{}".format(command))
        await self.controller.sendCommand(command)
        self.level = level

        

    async def triggerCallBacks(self, level:int):
        for cb in self.callBacks:
            cb()


   