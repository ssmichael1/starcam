import React, { useEffect, useState, useRef, useMemo} from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import { FrameHistogram } from './camclient';

import HCAnnot from "highcharts/modules/annotations";
import HCAnnotAdv from "highcharts/modules/annotations-advanced";

HCAnnot(Highcharts);
HCAnnotAdv(Highcharts);

const Histogram: React.FC<FrameHistogram> = ({ bins, hist }) => {
  const chartComponent = useRef<{
    chart: Highcharts.Chart;
    container: React.RefObject<HTMLDivElement>;
  }>(null); 

  const [an, setAn] = useState<Highcharts.Annotation>();
  const initialData = Array.from(Array(1024).keys()).map((v)=>[v*4, 0])

  const chartOptions: Highcharts.Options = {
    chart: {
      type: 'column',
      width: 1920/2,
      height: 500,
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

  } else {
    chart.addSeries({
      data: newData,
      color: 'blue',
      type: 'column'
    })
    let yl = chart.yAxis[0].getExtremes()
    
      
    setAn(chart.addAnnotation(
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
              console.log(e)
              let xValue = chart.xAxis[0].toValue(e?.chartX, false)
              console.log('Drag position x-axis value:', xValue);            }
          },
          draggable: 'x',
          shapes: [
            {
              type: "path",
              points: [
                {
                  x: 100,
                  y: yl.min,
                  xAxis: 0,
                  yAxis: 0
                },
                {
                  x: 100,
                  y: yl.max,
                  xAxis: 0,
                  yAxis: 0
                }
              ]
            }
          ]
        }
      )
    ) 
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