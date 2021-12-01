import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import { getEventEndpoint } from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

const StyledCard = styled.div`
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.primary100};
  padding: 1.5rem;
  margin: 2rem 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 1rem 0 0;
  }

  h5,
  p {
    margin: 0;
    padding: 0;
  }

  h5 {
    font-size: 1.125rem;
    font-weight: 600;
    line-height: 1.5;
    color: ${(props) =>
      props.$submitted ? props.theme.black1000 : props.theme.primary500};
  }

  p {
    font-size: 1rem;
    line-height: 1.6;
    padding: 0.25rem 0 1rem;
  }
`;

export const ReportFormCard = (props) => {
  const { title, description, url, submitted } = props;

  return (
    <StyledCard $submitted={submitted}>
      <h5>{title}</h5>
      {submitted ? (
        <p>
          <FeatherIcon inline name="check" /> Vous avez répondu à ce formulaire
        </p>
      ) : (
        <p>{description}</p>
      )}
      {!submitted && (
        <Button link small color="primary" href={url}>
          Je complète
        </Button>
      )}
    </StyledCard>
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
