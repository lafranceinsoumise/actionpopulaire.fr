import { animated, useSpring } from "@react-spring/web";
import PropTypes from "prop-types";
import React, { useEffect, useMemo, useRef } from "react";
import SwiperCore, { A11y, Pagination } from "swiper";
import { Swiper, SwiperSlide } from "swiper/react";
import styled from "styled-components";

import Announcement from "@agir/front/genericComponents/Announcement";

import style from "@agir/front/genericComponents/_variables.scss";
import "./Announcements.scss";
import useSWR from "swr";

SwiperCore.use([Pagination, A11y]);

export const SingleSlide = styled(animated.div)`
  margin: 0 1rem;
`;

export const Carousel = styled(animated.div)`
  .swiper-container {
    .swiper-slide {
      width: 80%;
      padding: 0 0.5rem;

      &:first-child {
        margin-left: 1.5rem;
        padding: 0;
      }

      &:last-child {
        margin-right: 1.5rem;
        padding: 0;
      }
    }
    .swiper-wrapper {
      margin-bottom: 1.5rem;
    }
    .swiper-pagination {
      text-align: left;
      bottom: 0;
      left: 1.5rem;

      .swiper-pagination-bullet-active {
        background-color: ${style.primary500};
      }
    }
  }
`;

export const BannerAnnouncements = (props) => {
  const { announcements } = props;
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

  if (announcements.length === 0) {
    return null;
  }

  if (announcements.length === 1) {
    return (
      <SingleSlide style={style}>
        <Announcement {...announcements[0]} />
      </SingleSlide>
    );
  }

  return announcements.length > 0 ? (
    <Carousel style={style}>
      <Swiper
        spaceBetween={16}
        slidesPerView="auto"
        pagination={{ clickable: true }}
      >
        {announcements.map((announcement) => (
          <SwiperSlide key={announcement.id}>
            <Announcement {...announcement} />
          </SwiperSlide>
        ))}
      </Swiper>
    </Carousel>
  ) : null;
};

const SidebarAnnouncements = (props) => {
  const { announcements } = props;

  return announcements.length > 0
    ? announcements.map((announcement) => (
        <Announcement key={announcement.id} {...announcement} />
      ))
    : null;
};

BannerAnnouncements.propTypes = SidebarAnnouncements.propTypes = {
  announcements: PropTypes.arrayOf(PropTypes.shape(Announcement.propTypes)),
};

const Announcements = (props) => {
  const { displayType } = props;
  const { data: announcements } = useSWR("/api/announcements/");

  if (!announcements) return null;

  return displayType === "sidebar" ? (
    <SidebarAnnouncements announcements={announcements} />
  ) : (
    <BannerAnnouncements announcements={announcements} />
  );
};
Announcements.propTypes = {
  displayType: PropTypes.oneOf(["sidebar", "banner"]),
};

export default Announcements;
