import React, { useEffect, useState, useRef, useMemo} from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import { FrameHistogram } from './camclient';

import HCAnnot from "highcharts/modules/annotations";
import HCAnnotAdv from "highcharts/modules/annotations-advanced";

HCAnnot(Highcharts);
HCAnnotAdv(Highcharts);

//const Histogram: React.FC<FrameHistogram> = ({ bins, hist }) => {
const Histogram: React.FC<{}> = () => {
  const chartComponent = useRef<{
    chart: Highcharts.Chart;
    container: React.RefObject<HTMLDivElement>;
  }>(null); 

  const initialData = Array.from(Array(1024).keys()).map((v)=>[v*4, 0])

  const chartOptions: Highcharts.Options = {chart: {
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
  series: [{
    data: initialData,
    color: 'blue',
    type: 'column'
  }],
  annotations: [
    {
      shapeOptions: {
        type: "path",
        dashStyle: "Solid",
        strokeWidth: 3,
        stroke: "red",
        fill: "red"
      },
      draggable: 'x',
      shapes: [
        {
          type: "path",
          points: [
            {
              x: 0,
              y: 25000,
              xAxis: 0,
              yAxis: 0
            },
            {
              x: 1000,
              y: 25000,
              xAxis: 0,
              yAxis: 0
            }
          ]
        }
      ]
    }
  ] 

  }

  /*
  useMemo(() => {
    if(!chartComponent.current)
      return;

    let chart = chartComponent.current?.chart

    //1console.log('redrawing')
    //console.log(chart.series)
    // chart.series[0].setData(bins.map((b,idx)=> [b, hist[idx]]))
    //chart.redraw(false)

  }, [bins, hist]);
  */

  console.log('redrawing')
  return (
    <HighchartsReact
      highcharts={Highcharts}
      options={chartOptions}
      ref={chartComponent}
    />
  );
};

export default Histogram;