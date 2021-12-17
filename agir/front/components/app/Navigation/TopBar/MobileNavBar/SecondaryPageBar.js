import PropTypes from "prop-types";
import React, { useState } from "react";

import { routeConfig } from "@agir/front/app/routes.config";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import RightLink from "./RightLink";
import StyledBar, { IconLink } from "./StyledBar";
import styled from "styled-components";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import ListUsers from "@agir/msgs/MessagePage/ListUsers";

import { useMessageSWR, useSelectMessage } from "@agir/msgs/common/hooks";
import { useRouteMatch } from "react-router-dom";

const StyledBlock = styled.div`
  display: flex;
  flex-direction: column;

  h2 {
    font-size: 16px;
    line-height: 1.5;
    font-weight: 500;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow-x: hidden;
    text-align: left;
    margin: 0;
  }
`;

const Description = styled.span`
  font-size: 12px;
`;

const defaultBackLink = {
  href: routeConfig.events.getLink(),
  to: routeConfig.events.getLink(),
  label: routeConfig.events.label,
};

const SecondaryPageBar = (props) => {
  const { isLoading, title, user, settingsLink } = props;
  const backLink = props.backLink || defaultBackLink;

  const matchMessagePage = useRouteMatch("/messages/:messagePk/");
  const messagePk = matchMessagePage?.params.messagePk;

  const onSelectMessage = useSelectMessage();
  const { currentMessage } = useMessageSWR(messagePk, onSelectMessage);

  const [openParticipants, setOpenParticipants] = useState(false);

  return (
    <StyledBar>
      <IconLink
        to={backLink.to}
        href={backLink.href}
        route={backLink.route}
        title={backLink.label}
        aria-label={backLink.label}
      >
        <RawFeatherIcon name="arrow-left" width="24px" height="24px" />
      </IconLink>

      <StyledBlock>
        <h2>{title}</h2>
        {!!matchMessagePage && (
          <Description onClick={() => setOpenParticipants(true)}>
            {currentMessage?.participants.total} participant·es &gt;
          </Description>
        )}
      </StyledBlock>

      {!!matchMessagePage && (
        <BottomSheet
          isOpen={openParticipants}
          onDismiss={() => setOpenParticipants(false)}
          shouldDismissOnClick
        >
          <ListUsers message={currentMessage} />
        </BottomSheet>
      )}

      <RightLink
        isLoading={isLoading}
        user={user}
        settingsLink={settingsLink}
      />
    </StyledBar>
  );
};

SecondaryPageBar.propTypes = {
  isLoading: PropTypes.bool,
  title: PropTypes.string,
  backLink: PropTypes.object,
  settingsLink: PropTypes.object,
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
};

export default SecondaryPageBar;
