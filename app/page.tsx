"use client";

import ImageView from "@/components/imageview";
import Histogram from "@/components/framehistogram";
import { WebSocketProvider, WebSocketContext } from "@/components/camclient";
import {useContext} from "react";

export default function Home() {
  // Assuming you have a 1D array of grayscale values
  
  const cols: number = 1920
  const rows: number = 1080
  const scale: number = 0.5

  //const [pixelData, setPixelData] = useState<number[]>(Array(rows*cols).fill(0))

  function Content() {
    const {data, frameInfo, frameHistogram} = useContext(WebSocketContext)
    if (data === null) {
      return (
        <div>Loading</div>
      )
    }
    return (
      <div className="items-start items-center">
        <div>Hi Steven</div>
        <ImageView pixelData={data} width={cols} height={rows} displayWidth={cols*scale} displayHeight={rows*scale} />
        <Histogram bins={frameHistogram.bins} hist={frameHistogram.hist} />
      </div>
    );
  }

   
  const {data} = useContext(WebSocketContext)
  return (
    <main className="flex min-h-screen flex-col items-start items-center justify-between p-24">
      <WebSocketProvider>
        <Content/>
      </WebSocketProvider>
  
    </main>

  );
}
