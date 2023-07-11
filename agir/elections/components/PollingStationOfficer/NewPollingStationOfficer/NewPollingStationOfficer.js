import React from "react";
import useSWRImmutable from "swr/immutable";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import Skeleton from "@agir/front/genericComponents/Skeleton";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import PollingStationOfficerForm from "./PollingStationOfficerForm";

import { getElectionEndpoint } from "@agir/elections/Common/api";

const NewPollingStationOfficer = () => {
  const { data: session } = useSWRImmutable("/api/session/");
  const { data: initialData } = useSWRImmutable(
    getElectionEndpoint("pollingStationOfficer"),
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
