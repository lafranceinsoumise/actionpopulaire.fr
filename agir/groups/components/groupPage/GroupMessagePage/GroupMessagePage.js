import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import CenteredLayout from "@agir/front/dashboardComponents/CenteredLayout";
import GroupMessage from "@agir/groups/groupPage/GroupMessage";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getBackLink } from "@agir/front/globalContext/reducers";

const StyledBlock = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  max-width: 580px;
  margin: 0 auto;
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    align-items: stretch;
  }
`;

const GroupMessagePage = (props) => {
  const {
    group,
    user,
    events,
    message,
    messageURL,
    groupURL,
    isLoading,
    loadMoreEvents,
    updateMessage,
    createComment,
    reportMessage,
    deleteMessage,
  } = props;

  const backLink = useSelector(getBackLink);

  return (
    <CenteredLayout backLink={backLink} desktopOnlyFooter={false}>
      <StyledBlock>
        <GroupMessage
          group={group}
          user={user}
          events={events}
          message={message}
          messageURL={messageURL}
          groupURL={groupURL}
          isLoading={isLoading}
          loadMoreEvents={loadMoreEvents}
          updateMessage={updateMessage}
          createComment={createComment}
          reportMessage={reportMessage}
          deleteMessage={deleteMessage}
        />
      </StyledBlock>
    </CenteredLayout>
  );
};
GroupMessagePage.propTypes = {
  group: PropTypes.object,
  events: PropTypes.arrayOf(PropTypes.object),
  loadMoreEvents: PropTypes.func,
  message: PropTypes.object,
  updateMessage: PropTypes.func,
  createComment: PropTypes.func,
  reportMessage: PropTypes.func,
  deleteMessage: PropTypes.func,
  user: PropTypes.object,
  messageURL: PropTypes.string,
  groupURL: PropTypes.string,
  isLoading: PropTypes.bool,
};

export default GroupMessagePage;
