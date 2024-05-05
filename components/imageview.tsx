"use client";

import React, { useRef, useEffect, useState } from 'react';

interface ImageViewProps {
  pixelData: number[];
  width: number;
  height: number;
  displayWidth: number;
  displayHeight: number;
}

const ImageView: React.FC<ImageViewProps> = ({ pixelData, width, height, displayWidth, displayHeight }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.imageSmoothingEnabled = false;
    ctx.imageSmoothingQuality = 'high';
  
    // Convert grayscale pixel data to RGBA pixel data
    const rgbaPixelData = pixelData.flatMap((value) => { 
      let v = Math.floor(value/16);
      return [v, v, v, 255]
    });
    const imageData = new ImageData(new Uint8ClampedArray(rgbaPixelData), width, height);
    ctx.putImageData(imageData, 0, 0);
  }, [pixelData, width, height]);


  return <canvas ref={canvasRef} width={width} height={height} style={{ width: `${displayWidth}px`, height: `${displayHeight}px` }} />;
};

export default ImageView;