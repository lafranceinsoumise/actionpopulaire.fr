import PropTypes from "prop-types";
import React from "react";
import { animated, useSpring } from "react-spring";
import styled from "styled-components";
import { A11y } from "swiper";
import { Swiper, SwiperSlide } from "swiper/react";

import MiniEventCard from "./MiniEventCard";

import "swiper/scss";
import "swiper/scss/a11y";

export const SingleSlide = styled(animated.div)`
  margin: 0;
`;

export const Carousel = styled(animated.div)`
  .swiper {
    .swiper-slide {
      width: auto;
      padding: 1px;
    }
    .swiper-wrapper {
      margin-bottom: 1.5rem;
    }
  }
`;

export const HorizontalLayout = (props) => {
  const { events } = props;
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
        <MiniEventCard {...events[0]} />
      </SingleSlide>
    );
  }

  return events.length > 0 ? (
    <Carousel style={style}>
      <Swiper spaceBetween={16} slidesPerView="auto" modules={[A11y]}>
        {events.map((event) => (
          <SwiperSlide key={event.id}>
            <MiniEventCard {...event} />
          </SwiperSlide>
        ))}
      </Swiper>
    </Carousel>
  ) : null;
};

const VerticalLayout = (props) => {
  const { events } = props;

  return events.length > 0
    ? events.map((event) => <MiniEventCard key={event.id} {...event} />)
    : null;
};

HorizontalLayout.propTypes = VerticalLayout.propTypes = {
  events: PropTypes.arrayOf(PropTypes.object),
};

const UpcomingEvents = (props) => {
  const { orientation = "horizontal", events } = props;

  if (events.length === 0) {
    return null;
  }

  if (orientation === "horizontal") {
    return <HorizontalLayout events={events} />;
  }

  if (orientation === "vertical") {
    return <VerticalLayout events={events} />;
  }

  return null;
};
UpcomingEvents.propTypes = {
  events: PropTypes.arrayOf(PropTypes.object),
  orientation: PropTypes.oneOf(["horizontal", "vertical"]),
};

export default UpcomingEvents;
