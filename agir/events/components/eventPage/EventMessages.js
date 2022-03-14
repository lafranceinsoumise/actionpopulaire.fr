import PropTypes from "prop-types";
import React, { useCallback, Fragment } from "react";

import styled from "styled-components";
import style from "@agir/front/genericComponents/_variables.scss";

import Spacer from "@agir/front/genericComponents/Spacer";
import MessageCard from "@agir/front/genericComponents/MessageCard";

import { getEventEndpoint } from "../common/api";
import useSWR from "swr";
import { getUser } from "@agir/front/globalContext/reducers";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { useHistory } from "react-router-dom";
import { routeConfig } from "@agir/front/app/routes.config";

const StyledH3 = styled.h3`
  @media (max-width: ${style.collapse}px) {
    padding-left: 1rem;
  }
`;

export const EventMessages = (props) => {
  const { eventPk } = props;

  console.log("event messages, event pk : ", eventPk);

  const user = useSelector(getUser);
  const { data: messages, error } = useSWR(
    getEventEndpoint("getEventMessages", { eventPk })
  );

  console.log("data messages : ", messages);

  const history = useHistory();

  const handleClickMessage = useCallback(
    (message) => {
      const link = routeConfig.messages.getLink({
        messagePk: message.id,
      });
      history?.push(link);
    },
    [history]
  );

  if (!messages?.length) {
    return <></>;
  }

  return (
    <>
      <StyledH3 style={{ marginTop: "2.5rem" }}>Messages</StyledH3>
      <article>
        {Array.isArray(messages) &&
          messages.map((message) => (
            <Fragment key={message.id}>
              <MessageCard
                user={user}
                message={message}
                comments={message.comments || message.recentComments || []}
                onClick={handleClickMessage}
                withBottomButton
              />
              <Spacer size="1.5rem" style={{ backgroundColor: "inherit" }} />
            </Fragment>
          ))}
      </article>
    </>
  );
};
EventMessages.propTypes = {
  eventPk: PropTypes.string,
};

export default EventMessages;
