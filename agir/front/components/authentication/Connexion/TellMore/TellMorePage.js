import React from "react";
import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { Redirect } from "react-router-dom";
import { useLocation } from "react-router-dom";

const TellMorePage = () => {
  const location = useLocation();
  const [hasCampaign, dismissCampaign] = useCustomAnnouncement(
    "chooseCampaign"
  );
  const [hasTellMore, dismissTellMore] = useCustomAnnouncement("tellMore");

  if (location.pathname !== "/bienvenue/" && (hasCampaign || hasTellMore))
    return <Redirect to="/bienvenue/" />;

  if (hasCampaign) return <ChooseCampaign dismiss={dismissCampaign} />;
  if (hasTellMore) return <TellMore dismiss={dismissTellMore} />;

  return <Redirect to="/" />;
};

export default TellMorePage;
