import React from "react";
import { useLocation } from "react-router-dom";
import useSWR from "swr";

import { routeConfig } from "@agir/front/app/routes.config";

import Announcement from "@agir/front/genericComponents/Announcement";

const Announcements = () => {
  const { pathname } = useLocation();

  const markAsDisplayed = routeConfig.activities.match(pathname) ? "0" : "1";

  const { data: announcements } = useSWR(
    "/api/announcements/?mark_as_displayed=" + markAsDisplayed,
  );

  if (!Array.isArray(announcements) || announcements.length === 0) return null;

  return announcements.map((announcement) => (
    <Announcement key={announcement.id} {...announcement} />
  ));
};

export default Announcements;
