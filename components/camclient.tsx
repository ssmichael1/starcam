import { AnyMxRecord } from 'dns';
import React, { createContext, useState, useEffect, ReactNode } from 'react';

export interface FrameInfo {
  timestamp: string;
  shape: number[];
  dtype: string;
}

export interface FrameHistogram {
  bins: number[];
  hist: number[];
}

interface WebSocketContextProps {
  data: number[];
  frameInfo: FrameInfo|null;
  frameHistogram: FrameHistogram;
}

interface WebSocketProviderProps {
  children: ReactNode;
}


const WebSocketContext = createContext<WebSocketContextProps>({ 
  data: Array(1920*1080).fill(0), 
  frameInfo: null, 
  frameHistogram: {
    bins: Array(1024).fill(0),
    hist: Array(1024).fill(0)
  }
})  ;

const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
    const [data, setData] = useState<any>(null);
    const [frameInfo, setFrameInfo] = useState<FrameInfo | null>(null);
    const [frameHistogram, setFrameHistogram] = useState<FrameHistogram>({bins: Array(1024).fill(0), hist: Array(1024).fill(0)});
    const [ws, setWs] = useState<WebSocket | null>(null);
  
    const frameHeader = 0xf8a3f8a3
    const frameinfoheader = 0x325a329a
    const framehistogramheader = 0x348da5f8

    useEffect(() => {
      const websocket = new WebSocket('ws://localhost:8001');
      websocket.binaryType = 'arraybuffer';
      setWs(websocket);
  
      websocket.onopen = () => {
        console.log('WebSocket is connected.');
      };
  
      websocket.onmessage = (event) => {
        if (websocket.readyState === WebSocket.OPEN) {
          let binary_header = new Uint8Array(event.data, 0, 4)
          let dv = new DataView(binary_header.buffer)
          let header = dv.getUint32(0, true)
          if (header === frameHeader) {
            let rawdata = new Uint16Array(event.data, 4)
            setData(Array.from(rawdata))
          }
          else if (header === frameinfoheader) {
            let frameinfo = JSON.parse(new TextDecoder().decode(new Uint8Array(event.data, 4)))
            setFrameInfo(frameinfo)
          }
          else if (header===framehistogramheader) {
            let bins = Array.from(new Uint32Array(event.data, 4, 1024))            
            let hist = Array.from(new Uint32Array(event.data, 4+1024*4, 1024))
            setFrameHistogram({bins:bins, hist:hist})
          }
        }
      };
  
      websocket.onerror = (error) => {
        console.log('WebSocket error: ', error);
      };
  
      websocket.onclose = (event) => {
        console.log('WebSocket is closed now.');
      };
  
      return () => {
        websocket.close();
      };
    }, []);
  
    return (
      <WebSocketContext.Provider value={{ data, frameInfo, frameHistogram }}>
        {children}
      </WebSocketContext.Provider>
    );
  };

export { WebSocketContext, WebSocketProvider };