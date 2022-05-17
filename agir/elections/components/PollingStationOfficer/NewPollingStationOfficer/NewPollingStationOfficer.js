import React from "react";
import useSWR from "swr";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import PollingStationOfficerForm from "./PollingStationOfficerForm";

import { getElectionEndpoint } from "@agir/elections/Common/api";
import { MANUAL_REVALIDATION_SWR_CONFIG } from "@agir/front/allPages/SWRContext";

const NewPollingStationOfficer = () => {
  const { data: session } = useSWR(
    "/api/session/",
    MANUAL_REVALIDATION_SWR_CONFIG
  );
  const { data: initialData } = useSWR(
    getElectionEndpoint("pollingStationOfficer", MANUAL_REVALIDATION_SWR_CONFIG)
  );

  return (
    <StyledPageContainer>
      <PageFadeIn
        ready={
          typeof session !== "undefined" && typeof initialData !== "undefined"
        }
        wait={
          <>
            <Spacer size="1rem" />
            <Skeleton />
          </>
        }
      >
        <PollingStationOfficerForm
          user={session?.user}
          initialData={initialData}
        />
      </PageFadeIn>
    </StyledPageContainer>
  );
};

export default NewPollingStationOfficer;
