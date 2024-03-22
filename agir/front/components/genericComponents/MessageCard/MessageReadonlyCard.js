import PropTypes from "prop-types";
import React, { useEffect, useMemo, useRef, useState } from "react";

import { formatEvent } from "@agir/events/common/utils";
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { timeAgo } from "@agir/lib/utils/time";
import { useCommentsSWR } from "@agir/msgs/common/hooks";
import { getMessageSubject } from "@agir/msgs/common/utils";

import Link from "@agir/front/app/Link";
import Comment from "@agir/front/formComponents/Comment";
import Avatar from "@agir/front/genericComponents/Avatar";
import Button from "@agir/front/genericComponents/Button";
import EventCard from "@agir/front/genericComponents/EventCard";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ParsedString from "@agir/front/genericComponents/ParsedString";
import { StyledLoader } from "@agir/msgs/MessagePage/MessageThreadMenu";
import MessageAttachment from "../../formComponents/MessageAttachment";
import MessageHeader from "./MessageHeader";
import {
  StyledComments,
  StyledContent,
  StyledGroupLink,
  StyledHeader,
  StyledLoadComments,
  StyledMessage,
  StyledPrivateVisibility,
  StyledWrapper,
} from "./StyledComponents";

const MessageReadonlyCard = (props) => {
  const { user, message, groupURL, isManager, backLink } = props;

  const { group, author, text, created, linkedEvent, lastUpdate, attachment } =
    message;

  const {
    comments,
    commentsCount,
    loadMore: loadMoreComments,
    isLoadingMore: isLoadingComments,
    mutate: mutateComments,
  } = useCommentsSWR(message.id, false);

  const messageCardRef = useRef();
  const isDesktop = useIsDesktop();

  const [loadedComments, setLoadedComments] = useState(false);
  const event = useMemo(() => formatEvent(linkedEvent), [linkedEvent]);

  const isAuthor = author.id === user.id;

  useEffect(() => {
    if (messageCardRef && !loadedComments) {
      messageCardRef.current.scrollTo(0, messageCardRef.current.scrollHeight);
      setLoadedComments(true);
    }
  }, [loadedComments]);

  useEffect(() => {
    lastUpdate && mutateComments && mutateComments();
  }, [lastUpdate, mutateComments]);

  const isPrivateMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.MEMBER;

  let subject = getMessageSubject(message);
  if (isPrivateMessage && !subject) {
    subject = `Message privé avec les animateur⋅ices de '${group.name}'`;
  }

  return (
    <>
      {isDesktop && (
        <MessageHeader readOnly subject={subject} message={message} />
      )}

      <StyledWrapper ref={messageCardRef}>
        {!isDesktop && <MessageHeader subject={subject} message={message} />}

        <StyledMessage>
          {isPrivateMessage && (
            <StyledPrivateVisibility>
              <RawFeatherIcon name={"eye"} style={{ paddingRight: "6px" }} />
              <div>
                Cette discussion privée se déroule entre{" "}
                {message.author.displayName} et les animateur·ices du groupe{" "}
                <StyledGroupLink to={groupURL}>{group.name}</StyledGroupLink>
              </div>
            </StyledPrivateVisibility>
          )}

          <StyledHeader>
            <Avatar {...author} />
            <h4>
              <strong>
                {author.displayName || (isAuthor && "Moi") || "Quelqu'un"}
                &nbsp;
                {!author.displayName && isAuthor && (
                  <Link route="personalInformation">Ajouter mon nom</Link>
                )}
              </strong>
              <em>{created ? timeAgo(created) : null}</em>
              {groupURL && group && group.name ? (
                <StyledGroupLink to={groupURL}>{group.name}</StyledGroupLink>
              ) : null}
            </h4>
          </StyledHeader>

          <StyledContent>
            <ParsedString>{text}</ParsedString>
          </StyledContent>

          <MessageAttachment file={attachment?.file} name={attachment?.name} />

          {!!event && <EventCard {...event} />}

          <StyledComments $empty={!comments?.length}>
            <PageFadeIn ready={comments.length > 0}>
              {isLoadingComments && <StyledLoader loading block />}
              {!isLoadingComments && commentsCount !== comments.length && (
                <StyledLoadComments onClick={loadMoreComments}>
                  <RawFeatherIcon
                    name="chevron-up"
                    width="1rem"
                    height="1rem"
                  />
                  {commentsCount - comments.length} commentaires précédents
                </StyledLoadComments>
              )}
              {comments.map((comment) => (
                <Comment
                  key={comment.id}
                  comment={comment}
                  isAuthor={comment.author.id === user.id}
                  isManager={isManager}
                />
              ))}
            </PageFadeIn>
          </StyledComments>

          <div style={{ textAlign: "center" }}>
            <Button
              link
              small
              icon="eye"
              route="messages"
              routeParams={{ messagePk: message.id }}
              color="secondary"
              backLink={backLink}
            >
              Voir la conversation
            </Button>
          </div>
        </StyledMessage>
      </StyledWrapper>
    </>
  );
};

MessageReadonlyCard.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.string.isRequired,
    image: PropTypes.string,
  }).isRequired,
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    group: PropTypes.shape({
      name: PropTypes.string,
    }),
    author: PropTypes.shape({
      id: PropTypes.string.isRequired,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    created: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    linkedEvent: PropTypes.object,
    lastUpdate: PropTypes.string,
    attachment: PropTypes.shape({
      file: PropTypes.string,
      name: PropTypes.string,
    }),
    isLocked: PropTypes.bool,
    readonly: PropTypes.bool,
    requiredMembershipType: PropTypes.number,
  }).isRequired,
  groupURL: PropTypes.string,
  isManager: PropTypes.bool,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default MessageReadonlyCard;
