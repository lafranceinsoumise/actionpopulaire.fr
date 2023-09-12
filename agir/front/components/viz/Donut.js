import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";


import style from "@agir/front/genericComponents/_variables.scss";

import {pie, arc} from "d3-shape";
import {scaleOrdinal} from "d3-scale";
import {color as d3color} from "d3-color";

const DEFAULT_COLORS = [
  style.nupesBlue,
  style.nupesRed,
  style.nupesPink,
  style.nupesGreen,
  style.nupesYellow,
]


export const Section = ({arc, data, colorScale}) => {
  const [hover, setHover] = useState(false);

  const baseColor = colorScale(data.data.label);
  const color = hover ? d3color(baseColor).darker().formatHex() : baseColor;

  return <path d={arc(data)} fill={color} onMouseOver={() => setHover(true)} onMouseLeave={()=>setHover(false)} />;
}

Section.propTypes = {
  arc: PropTypes.func,
  data: PropTypes.shape({
    startAngle: PropTypes.number,
    endAngle: PropTypes.number
  })
};

export const Donut = ({data, padAngle, colorScale, size }) => {
  const sections = useMemo(() => {
     let p = pie().value(d => d.value);
     if (padAngle) {
       p = p.padAngle(padAngle);
     }
     return p(data);
    }, [data, padAngle]
  )

  const actualColorScale = useMemo(() => colorScale || scaleOrdinal(data.map(d => d.label), DEFAULT_COLORS), [colorScale, data])

  const arcFunc = useMemo(() => arc().innerRadius(0.25 * size).outerRadius(0.43 * size))

  return <svg height={size} width={size}>
    <g className="sections" transform={`translate(${size/2}, ${size/2})`}>
    {sections.map((s, i) => <Section key={i} arc={arcFunc} data={s} colorScale={actualColorScale}/>)}
    </g>
  </svg>
};
Donut.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string,
    value: PropTypes.number,
  })).isRequired,
  padAngle: PropTypes.number,
  colorScale: PropTypes.func,
  size: PropTypes.number.isRequired
};
Donut.defaultProps = {
  padAngle: Math.PI * 6e-3,
}

export default Donut;
