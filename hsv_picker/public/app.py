#!/usr/bin/env python

import asyncio
import websockets

my_port = 8000

async def handler(websocket):
    img = open('toMask.jpg', 'rb')
    websocket.send_binary(img.open())
    while True:
        try:
            print("Up and running!")
        except websockets.ConnectionClosedOK:
            break


async def main():
    async with websockets.serve(handler, "", my_port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    print(f"Socket on port {my_port}")
    asyncio.run(main())