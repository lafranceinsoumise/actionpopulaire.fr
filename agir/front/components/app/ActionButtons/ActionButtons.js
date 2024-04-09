import PropTypes from "prop-types";
import React, { useMemo } from "react";
import { animated, useSpring } from "@react-spring/web";
import styled from "styled-components";
import { Swiper, SwiperSlide } from "swiper/react";
import useSWR from "swr";

import "swiper/scss";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { getActionsForUser } from "./actions.config";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import ActionButton from "./ActionButton";

const Carousel = styled(animated.div)`
  position: relative;
  isolation: isolate;
  margin: 0 -1rem;
  width: calc(100% + 2rem);

  & > * {
    z-index: 0;
  }

  .swiper-slide {
    padding: 0 4px;

    &:first-child {
      padding-left: 16px;
    }

    &:last-child {
      padding-right: 16px;
    }
  }

  &::before,
  &::after {
    content: "";
    display: block;
    position: absolute;
    top: 0;
    bottom: 0;
    height: 100%;
    width: 16px;
    z-index: 1;
    pointer-events: none;
  }

  &::before {
    left: 0;
    background: linear-gradient(90deg, ${style.black25}, ${style.black25}00);
  }

  &::after {
    right: 0;
    background: linear-gradient(-90deg, ${style.black25}, ${style.black25}00);
  }
`;

const StyledActionList = styled.nav`
  width: 100%;
  display: flex;
  flex-flow: column nowrap;
  gap: 0.5rem;
  min-height: 1px;
  padding: 0;
  margin: 0;
`;

const getSwiperBreakpoints = (slides = [], slideWidth) => {
  const breakpoints = {};
  for (
    let breakpoint = style.collapse, slidesPerView = slides.length;
    breakpoint > 0 && slidesPerView >= 3;
    breakpoint -= slideWidth
  ) {
    slidesPerView = Math.ceil(breakpoint / slideWidth) - 0.5;
    breakpoints[breakpoint] = {
      slidesPerView,
    };
  }
  return breakpoints;
};

export const ActionButtonCarousel = (props) => {
  const { actions } = props;
  const breakpoints = useMemo(
    () => getSwiperBreakpoints(actions, 75 + 8),
    [actions],
  );

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

  return (
    <Carousel style={style}>
      <Swiper
        slidesPerView={3}
        breakpoints={breakpoints}
        centerInsufficientSlides
      >
        {actions
          .filter((action) => !action.disabled)
          .map((action) => (
            <SwiperSlide key={action.key}>
              <ActionButton {...action} />
            </SwiperSlide>
          ))}
      </Swiper>
    </Carousel>
  );
};
ActionButtonCarousel.propTypes = {
  actions: PropTypes.arrayOf(PropTypes.object),
};

const ActionButtonList = ({ actions }) => (
  <StyledActionList>
    {actions.map((action) => (
      <ActionButton key={action.key} {...action} />
    ))}
  </StyledActionList>
);
ActionButtonList.propTypes = {
  actions: PropTypes.arrayOf(PropTypes.object),
};

export const ActionButtons = ({ user }) => {
  const actions = getActionsForUser(user);

  return (
    <ResponsiveLayout
      MobileLayout={ActionButtonCarousel}
      DesktopLayout={ActionButtonList}
      actions={actions}
    />
  );
};
ActionButtons.propTypes = {
  user: PropTypes.object,
};

const ConnectedActionButtons = () => {
  const { data: session } = useSWR("/api/session/");
  return <ActionButtons user={session?.user} />;
};

export default ConnectedActionButtons;
