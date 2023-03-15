import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";
import { Swiper, SwiperSlide } from "swiper/react";

import MiniEventCard from "./MiniEventCard";

import "swiper/scss";
import { rest } from "lodash/fp";

export const SingleSlide = styled(animated.div)`
  margin: 0;
`;

export const Carousel = styled(animated.div)`
  .swiper {
    .swiper-slide {
      box-sizing: border-box;
      width: auto;
      padding: 1px;
    }
  }
`;

export const HorizontalLayout = (props) => {
  const { events, ...rest } = props;
  const style = useSpring({
    from: {
      opacity: 0,
      paddingLeft: 24,
    },
    to: {
      opacity: 1,
      paddingLeft: 0,
    },
  });

  if (events.length === 1) {
    return (
      <SingleSlide style={style}>
        <MiniEventCard {...rest} {...events[0]} />
      </SingleSlide>
    );
  }

  return events.length > 0 ? (
    <Carousel style={style}>
      <Swiper spaceBetween={16} slidesPerView="auto">
        {events.map((event) => (
          <SwiperSlide key={event.id}>
            <MiniEventCard {...rest} {...event} />
          </SwiperSlide>
        ))}
      </Swiper>
    </Carousel>
  ) : null;
};

const VerticalLayout = (props) => {
  const { events, ...rest } = props;

  return events.length > 0
    ? events.map((event) => (
        <MiniEventCard key={event.id} {...rest} {...event} />
      ))
    : null;
};

HorizontalLayout.propTypes = VerticalLayout.propTypes = {
  events: PropTypes.arrayOf(PropTypes.object),
};

const UpcomingEvents = (props) => {
  const { orientation = "horizontal", ...rest } = props;

  if (props.events.length === 0) {
    return null;
  }

  if (orientation === "horizontal") {
    return <HorizontalLayout {...rest} />;
  }

  if (orientation === "vertical") {
    return <VerticalLayout {...rest} />;
  }

  return null;
};
UpcomingEvents.propTypes = {
  events: PropTypes.arrayOf(PropTypes.object),
  orientation: PropTypes.oneOf(["horizontal", "vertical"]),
};

export default UpcomingEvents;
