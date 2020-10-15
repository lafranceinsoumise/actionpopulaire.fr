import styled from "styled-components";
import PropTypes from "prop-types";
import Card from "./Card";
import style from "./style.scss";

/**
 * Accessibility
 */

export const SROnly = styled.span`
  border: 0 !important;
  clip: rect(1px, 1px, 1px, 1px) !important;
  -webkit-clip-path: inset(50%) !important;
  clip-path: inset(50%) !important;
  height: 1px !important;
  overflow: hidden !important;
  padding: 0 !important;
  position: absolute !important;
  width: 1px !important;
  white-space: nowrap !important;
`;

/**
 * Text
 */
export const Center = styled.div`
  text-align: center;
`;

export const Right = styled.div`
  text-align: right;
`;

export const PullRight = styled.div`
  float: right;
`;

/**
 * Media queries
 */
export const Hide = styled.div`
  @media (max-width: ${({ under }) => under}px) {
    display: none;
  }

  @media (min-width: ${({ over }) => over}px) {
    display: none;
  }
`;

/**
 * Grid
 */

const gutter = 32;
const collapse = 992;

export const GrayBackgrund = styled.div`
  background-color: ${style.pageBackgroundColor};
`;

export const Container = styled.section`
  width: ${1100 + gutter * 2}px;
  max-width: 100%;
  margin: 0 auto;
  padding-left: ${gutter}px;
  padding-right: ${gutter}px;
`;

export const Column = styled.div`
  flex-basis: ${({ width, fill }) => (width || fill ? width || "1px" : "auto")};
  flex-grow: ${({ fill }) => (fill ? 1 : 0)};
  & > ${Card} {
    margin-bottom: 16px;
  }

  @media (max-width: ${(props) =>
      typeof props.collapse === "undefined"
        ? collapse
        : props.collapse || 0}px) {
    min-width: 100%;
    padding-left: 0;
    padding-right: 0;

    & > ${Card} {
      margin-bottom: 0px;
    }
  }
`;

Column.propTypes = {
  width: PropTypes.string, // can be anything like "50%" "400px"
  fill: PropTypes.bool, // does the column fill the remaining space
};

export const Row = styled.div`
  margin-left: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
  margin-right: -${(props) => (typeof props.gutter === "undefined" ? gutter : props.gutter)}px;
  display: flex;
  flex-wrap: wrap;
  align-items: ${({ align }) => align || "stretch"};
  justify-content: ${({ justify }) => justify || "start"};
  height: 100%;

  & > ${Column} {
    padding-left: ${(props) =>
      typeof props.gutter === "undefined" ? gutter : props.gutter}px;
    padding-right: ${(props) =>
      typeof props.gutter === "undefined" ? gutter : props.gutter}px;
  }
`;

Row.propTypes = {
  children: PropTypes.arrayOf(PropTypes.instanceOf(Column)),
  align: PropTypes.arrayOf([
    "stretch",
    "baseline",
    "center",
    "flex-start",
    "flex-end",
  ]), // align-items CSS property
  justify: PropTypes.arrayOf([
    "flex-start",
    "flex-end",
    "center",
    "space-between",
    "space-around",
    "space-evenly",
  ]), // justify-content CSS property
};
