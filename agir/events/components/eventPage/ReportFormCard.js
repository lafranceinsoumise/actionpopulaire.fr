import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import { getEventEndpoint } from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import StyledCard from "./StyledCard";

const StyledReportCard = styled(StyledCard)`
  background-color: ${(props) => props.theme.primary100};

  h5 {
    color: ${(props) =>
      props.$submitted ? props.theme.black1000 : props.theme.primary500};
  }

  p + ${Button} {
    margin-top: 1rem;
  }
`;

export const ReportFormCard = (props) => {
  const { title, description, url, submitted } = props;

  return (
    <StyledReportCard $submitted={submitted}>
      <h5>{title}</h5>
      {submitted ? (
        <p>
          <FeatherIcon inline name="check" /> Vous avez répondu à ce formulaire
        </p>
      ) : (
        <p dangerouslySetInnerHTML={{ __html: description }} />
      )}
      {!submitted && (
        <Button link small color="primary" href={url}>
          Je complète
        </Button>
      )}
    </StyledReportCard>
  );
};

ReportFormCard.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  url: PropTypes.string.isRequired,
  submitted: PropTypes.bool.isRequired,
};

const ConnectedReportFormCard = ({ eventPk }) => {
  const { data } = useSWR(
    eventPk && getEventEndpoint("getEventReportForm", { eventPk })
  );
  return (
    <PageFadeIn ready={!!data?.url}>
      {data && (
        <ReportFormCard
          title={data?.title}
          description={data?.description}
          url={data?.url}
          submitted={data?.submitted}
        />
      )}
    </PageFadeIn>
  );
};

ReportFormCard.propTypes = {
  eventPk: PropTypes.string.isRequired,
};

export default ConnectedReportFormCard;
