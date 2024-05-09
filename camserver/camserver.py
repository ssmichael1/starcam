#!/usr/bin/env python3

# %%
import asyncio
import json
import sys
import base64
from svb import *
from svb_sdk import SVB_IMG_TYPE
import os
from socketify import App, OpCode, CompressOptions
from threading import Thread
import time

clients = set()

frameheader = 0xf8a3f8a3
frameinfoheader = 0x325a329a
framehistogramheader = 0x348da5f8

started = False

client_lock = asyncio.Lock()
app = App()    

def compute_histogram(frame):
    hist, bins = np.histogram(frame, bins=1024, range=(0, 4096))
    bins = (bins[1:] + bins[:-1]) / 2
    hist[-1] = 0
    return hist, bins


async def callback(frame, timestamp):
    frame = np.right_shift(frame, 4)
    # Prepare data
    hist, bins  = compute_histogram(frame)
    frameinfo = frameinfoheader.to_bytes(4, 'little') + json.dumps({
        'timestamp': timestamp.isoformat(),
        'shape': frame.shape,
        'dtype': str(frame.dtype),
    }).encode('utf-8')
    senddata = frameheader.to_bytes(4, 'little') + frame.tobytes()
    
    framehistogram = framehistogramheader.to_bytes(4, 'little') + \
                    bins.astype(np.uint32).tobytes() + \
                    hist.astype(np.uint32).tobytes()

    if len(clients)==0:        
        return
    
    async with client_lock:
        for client in list(clients):
            try:            
                client.send(frameinfo)
                client.send(framehistogram)
                client.send(senddata)
            except Exception as e:
                print(f"Error sending message to client: {e}")


async def simcam():
    [x,y] = np.meshgrid(np.arange(-960, 960), np.arange(-540, 540 ))  
    sigma = 125
    time.sleep(1)

    fname = './fixed_25mm__000007__21-33-42__data.ser'
    if os.path.exists(fname):
        from ser import SERFile
        serdata = SERFile(fname)
        print(serdata.frame_count)
        idx = 0
        while True:
            frame = serdata.frame(idx)
            idx += 1
            if idx >= serdata.frame_count:
                idx = 0
            timestamp = dt.datetime.now()
            await callback(frame, timestamp)
            await asyncio.sleep(0.06)
    else:
        while True:
            cen = np.random.rand(2)*100
            frame = 2048 * np.exp(-((x-cen[0])**2 + (y-cen[1])**2)/(2*sigma**2))
            frame = frame + 512.0 + np.random.random()*128 + np.random.randn(1080, 1920)*128
            frame = (frame * 16).astype(np.uint16)        
            timestamp = dt.datetime.now()
            await callback(frame, timestamp)
            await asyncio.sleep(0.1)



async def ws_open(ws):
    global started
    global client_lock
    print('A WebSocket got connected!')    
    
    async with client_lock:
        clients.add(ws)
    
    if started == False:
        print(f'starting sim task')
        started = True
        asyncio.create_task(simcam())

async def ws_close(ws, code, message):
    print('A WebSocket got closed! Code:', code, 'Message:', message)
    async with client_lock:
        clients.remove(ws)

async def ws_message(ws, message, opcode):
    pass
    #Ok is false if backpressure was built up, wait for drain
    # ok = ws.send(message, opcode)



#app.on_start(app.loop.create_task(simcam()))
# app.on_start(asyncio.#)

app.ws("/*", {
    'compression': CompressOptions.SHARED_COMPRESSOR,
    'max_payload_length': 64 * 1024 * 1024,
    'idle_timeout': 12,''
    'open': ws_open,
    'message': ws_message,
    'drain': lambda ws: print(f'WebSocket backpressure: {ws.get_buffered_amount()}'),
    'close': ws_close,
    'on_start': lambda ws: print(f'WebSocket started: {ws}'),
    #'subscription': lambda ws, topic, subscriptions, subscriptions_before: print(f'subscribe/unsubscribe on topic {topic} {subscriptions} {subscriptions_before}'),
})
app.any("/", lambda res,req: res.end("Nothing to see here!'"))
app.listen(8001, lambda config: print("Listening on port http://localhost:%d\n" % (config.port)))
#app.loop.create_task(simcam()))
app.run()


#cbdata = {
#    'loop': asyncio.get_running_loop(),
#    'last_send_time': dt.datetime.now(),
#}
#task = asyncio.create_task(simcam(cbdata))




