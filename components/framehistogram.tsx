import React, { useEffect, useState, useRef, useMemo} from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import { FrameHistogram } from './camclient';

import HCAnnot from "highcharts/modules/annotations";
import HCAnnotAdv from "highcharts/modules/annotations-advanced";
import { minifySync } from 'next/dist/build/swc';

if (typeof Highcharts === 'object') {
  HCAnnot(Highcharts);
  HCAnnotAdv(Highcharts);
}


interface FrameHistogramFCData {
  minfc: number;
  maxfc: number;
  gamma: number;
}

const Histogram: React.FC<FrameHistogram> = ({ bins, hist }) => {
  const chartComponent = useRef<{
    chart: Highcharts.Chart;
    container: React.RefObject<HTMLDivElement>;
  }>(null); 

  const [anLimLeft, setAnLimLeft] = useState<Highcharts.Annotation>();
  const [anLimRight, setAnLimRight] = useState<Highcharts.Annotation>();
  const initialData = Array.from(Array(1024).keys()).map((v)=>[v*4, 0])
  
  let fcData: FrameHistogramFCData = {minfc: 0, maxfc: 1, gamma: 1.0}
  let anLeftLim: Highcharts.Annotation|null = null
  let anRightLim: Highcharts.Annotation|null = null

  const chartOptions: Highcharts.Options = {
    chart: {
      type: 'column',
      width: 1920/2,
      height: 500,
      animation: false,
    },
    title: {
      text: 'Histogram'
    },
    xAxis: {
      min: 0, 
      max: 4096,
    },
    plotOptions: {
      series: {
        animation: false,
      },
    },
    legend: {
      align: 'right',
      verticalAlign: 'top',
      x: -10,
      y: 100,
      floating: true,
    }      
  }

// In your useMemo hook
useEffect(() => {
  if(!chartComponent.current)
    return;

  let chart = chartComponent.current.chart;

  // Assuming bins and hist are your new data
  let newData = bins.map((b,idx) => [b, hist[idx]]);

  if (chart.series.length > 0) {
    chart.series[0].setData(newData);
    chart.redraw(false)
  } else {
    chart.addSeries({
      data: newData,
      color: 'blue',
      type: 'column',
      name: 'Histogram'
    })
    /*
    let yl = chart.yAxis[0].getExtremes()
    let xl = chart.xAxis[0].getExtremes()
    console.log('xl = ' + xl.min + ' ' + xl.max)
    fcData = {...fcData, minfc: xl.min, maxfc: xl.max}
    console.log(fcData)

    setAnLimRight(chart.addAnnotation(
      {
        shapeOptions: {
          type: "path",
          dashStyle: "Solid",
          strokeWidth: 3,
          stroke: "green",
          fill: "green"
        },
        events: {
          drag: (e: any) => {
            let xValue = chart.xAxis[0].toValue(e?.chartX, false)
            if (xValue < fcData.minfc + 8) {
              console.log('preventing movement')
              xValue = fcData.minfc + 8
              let xPixelValue = chart.xAxis[0].toPixels(xValue, false)
              console.log('xPixelValue = ' + xPixelValue)
              anLimRight?.shapesGroup.attr({x: xPixelValue})
              return
            }
            fcData = {...fcData, maxfc: xValue};
          },
    
        },
        draggable: 'x',
        shapes: [
          {
            type: "path",
            points: [
              {
                x: 3000,
                y: yl.min,
                xAxis: 0,
                yAxis: 0
              },
              {
                x: 3000,
                y: yl.max,
                xAxis: 0,
                yAxis: 0
              }
            ]
          }
        ]
      }
    ))
      
    setAnLimLeft(chart.addAnnotation(
        {
          shapeOptions: {
            type: "path",
            dashStyle: "Solid",
            strokeWidth: 3,
            stroke: "red",
            fill: "red"
          },
          events: {
            drag: (e: any) => {
              let xValue = chart.xAxis[0].toValue(e?.chartX, false)
              if (xValue > fcData.maxfc - 8) {
                xValue = fcData.maxfc - 8
              }
              
              fcData = {...fcData, minfc: xValue};
            }
          },
          draggable: 'x',
          shapes: [
            {
              type: "path",
              points: [
                {
                  x: xl.min,
                  y: yl.min,
                  xAxis: 0,
                  yAxis: 0
                },
                {
                  x: xl.min,
                  y: yl.max,
                  xAxis: 0,
                  yAxis: 0
                }
              ]
            }
          ]
        }
      ))
    */      
  }
}, [bins, hist]);

  return (
    <HighchartsReact
      highcharts={Highcharts}
      options={chartOptions}
      ref={chartComponent}
    />
  );
};

export default Histogram;