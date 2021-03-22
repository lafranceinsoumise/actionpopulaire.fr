import React, { useState, useEffect } from "react";
import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { Redirect } from "react-router-dom";
import { getProfile } from "@agir/front/authentication/api";

const TellMorePage = () => {
  const [hasCampaign, dismissCampaign] = useCustomAnnouncement(
    "chooseCampaign"
  );
  const [hasTellMore, dismissTellMore] = useCustomAnnouncement("tellMore");

  console.log("usecustom : ", hasCampaign, hasTellMore);

  if (hasCampaign) return <ChooseCampaign dismiss={dismissCampaign} />;
  if (hasTellMore) return <TellMore dismiss={dismissTellMore} />;

  return <Redirect to="/" />;
};

export default TellMorePage;
