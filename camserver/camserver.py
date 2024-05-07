#!/usr/bin/env python3

# %%
import asyncio
import json
import websockets
import sys
import base64
from svb import *
from svb_sdk import SVB_IMG_TYPE

clients = set()

frameheader = 0xf8a3f8a3
frameinfoheader = 0x325a329a
framehistogramheader = 0x348da5f8

def compute_histogram(frame):
    hist, bins = np.histogram(frame, bins=1024, range=(0, 4096))
    bins = (bins[1:] + bins[:-1]) / 2
    hist[-1] = 0
    return hist, bins





def callback(frame, timestamp, cbdata):

    cbdata['frametime'] = timestamp
    frame = np.right_shift(frame, 4)

    async def broadcast(frame, cbdata):
        
        if (cbdata['frametime'] - cbdata['last_send_time']).total_seconds() < 0.15:
            return

        if clients:  # guard against an empty set
            for client in list(clients):
                try:
                    hist, bins  = compute_histogram(frame)
                    await client.send(frameinfoheader.to_bytes(4, 'little') + json.dumps({
                        'timestamp': cbdata['frametime'].isoformat(),
                        'shape': frame.shape,
                        'dtype': str(frame.dtype),
                    }).encode('utf-8'))
                    await client.send(frameheader.to_bytes(4, 'little') + frame.tobytes())
                    await client.send(framehistogramheader.to_bytes(4, 'little') + 
                                      bins.astype(np.uint32).tobytes() + 
                                      hist.astype(np.uint32).tobytes())
                    cbdata['last_send_time'] = dt.datetime.now()

                except Exception as e:
                    print(f"Error sending message to client: {e}")
                    #clients.remove(client)

    # Pass the coroutine object to run_coroutine_threadsafe, not the result of calling it
    asyncio.run_coroutine_threadsafe(broadcast(frame, cbdata), cbdata['loop'])

async def simcam(cbdata):
    [x,y] = np.meshgrid(np.arange(-960, 960), np.arange(-540, 540 ))  
    sigma = 125



    while True:
        cen = np.random.rand(2)*100
        frame = 2048 * np.exp(-((x-cen[0])**2 + (y-cen[1])**2)/(2*sigma**2))
        frame = frame + 512.0 + np.random.randn(1080, 1920)*128
        frame = (frame * 16).astype(np.uint16)

     
        timestamp = dt.datetime.now()
        callback(frame, timestamp, cbdata)
        await asyncio.sleep(0.1)

async def handler(websocket, path):
    clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            message = await websocket.recv()
            print(message)
    except Exception as e:
        print(f"Error receiving message from client: {e}")
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    loop = asyncio.get_running_loop()

    cbdata = {
        'loop': loop,
        'last_send_time': dt.datetime.now(),
    }

    cameras = svb_get_connected_cameras()
    if len(cameras) == 0:
        print("No cameras found; running simulated camera")
        task = asyncio.create_task(simcam(cbdata))

    else:
        camera = SVBonyCamera(0)
        print(f'Exposure: {camera.exposure}')
        camera.exposure = 100000
        print(f'Exposure: {camera.exposure}')
        camera.gain = 10
        camera.output_image_type = SVB_IMG_TYPE.SVB_IMG_Y16
        camera.frame_speed_mode = 0
        camera.add_callback(lambda frame, timestamp: callback(frame, timestamp, cbdata))
        camera.start_capture()

    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())