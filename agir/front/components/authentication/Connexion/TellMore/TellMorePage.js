import React, { useCallback, useEffect, useState } from "react";
import { Redirect, useRouteMatch, useLocation } from "react-router-dom";
import useSWRImmutable from "swr/immutable";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

import TellMore from "./TellMore";
import ChooseCampaign from "./ChooseCampaign";
import ChooseNewsletters from "./ChooseNewsletters";

const TellMorePage = () => {
  const location = useLocation();
  const isTellMorePage = useRouteMatch(routeConfig.tellMore.getLink());

  const { data: session } = useSWRImmutable("/api/session/");

  const [hasCampaign, dismissCampaign, campaignIsLoading] =
    useCustomAnnouncement("chooseCampaign", false);

  const [hasNewsletters, dismissNewsletters, newslettersAreLoading] =
    useCustomAnnouncement("ChooseNewsletters", false);

  const [hasTellMore, dismissTellMore, tellMoreIsLoading] =
    useCustomAnnouncement("tellMore", false);

  if (!isTellMorePage && (hasCampaign || hasNewsletters || hasTellMore)) {
    return <Redirect to={routeConfig.tellMore.getLink()} />;
  }

  if (
    !isTellMorePage ||
    campaignIsLoading ||
    tellMoreIsLoading ||
    newslettersAreLoading
  ) {
    return null;
  }

  if (hasCampaign) {
    return (
      <ChooseCampaign
        fromSignup={location.hash && location.hash.includes("agir_id")}
        dismiss={dismissCampaign}
      />
    );
  }

  if (hasNewsletters) {
    return (
      <ChooseNewsletters dismiss={dismissNewsletters} user={session?.user} />
    );
  }

  if (hasTellMore) {
    return <TellMore dismiss={dismissTellMore} />;
  }

  return <Redirect to={routeConfig.events.getLink()} />;
};

export default TellMorePage;
