import React from "react";
import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { Redirect } from "react-router-dom";

const TellMorePage = () => {
  const [hasCampaign, dismissCampaign] = useCustomAnnouncement(
    "chooseCampaign"
  );
  const [hasTellMore, dismissTellMore] = useCustomAnnouncement("tellMore");

  if (hasCampaign) return <ChooseCampaign dismiss={dismissCampaign} />;
  if (hasTellMore) return <TellMore dismiss={dismissTellMore} />;

  return <Redirect to="/" />;
};

export default TellMorePage;
