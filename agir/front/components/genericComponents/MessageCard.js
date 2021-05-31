import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import styled from "styled-components";

import { FaWhatsapp, FaTelegram } from "react-icons/fa";

import style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";
import { formatEvent } from "@agir/events/common/utils";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import Avatar from "@agir/front/genericComponents/Avatar";
import Card from "@agir/front/genericComponents/Card";
import EventCard from "@agir/front/genericComponents/EventCard";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ParsedString from "@agir/front/genericComponents/ParsedString";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import CommentField, {
  CommentButton,
} from "@agir/front/formComponents/CommentField";
import Comment from "@agir/front/formComponents/Comment";

const StyledInlineMenuItems = styled.div`
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${style.primary500};
  padding: 0;

  @media (max-width: ${style.collapse}px) {
    margin: 0;
    padding: 1.5rem;
  }

  & > span {
    font-size: 0.875rem;
    line-height: 20px;
    font-weight: 400;
    color: ${style.black1000};
    margin-bottom: 0.5rem;

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 1.5rem;
    }
  }

  a,
  button {
    display: flex;
    align-items: center;
    border: none;
    padding: 0;
    margin: 0;
    text-decoration: none;
    background: inherit;
    cursor: pointer;
    text-align: center;
    -webkit-appearance: none;
    -moz-appearance: none;
    font-size: 0.875rem;
    line-height: 20px;
    font-weight: 400;
    color: ${style.black1000};
    margin-bottom: 0.5rem;

    &:last-child {
      margin-bottom: 0;
    }

    &:hover,
    &:focus {
      text-decoration: underline;
      border: none;
      outline: none;
    }

    &[disabled],
    &[disabled]:hover,
    &[disabled]:focus {
      opacity: 0.75;
      text-decoration: none;
      cursor: default;
    }

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 1.5rem;
      text-decoration: none;
    }

    & > *:first-child {
      margin-right: 0.5rem;
      width: 1rem;
      height: 1rem;

      @media (max-width: ${style.collapse}px) {
        margin-right: 1rem;
        width: 1.5rem;
        height: 1.5rem;
      }

      svg {
        width: inherit;
        height: inherit;
        stroke-width: 2;
      }
    }
  }
`;
const StyledAction = styled.div`
  & > button {
    border: none;
    padding: 0;
    margin: 0;
    text-decoration: none;
    background: inherit;
    cursor: pointer;
    text-align: center;
    -webkit-appearance: none;
    -moz-appearance: none;
  }
`;
const StyledGroupLink = styled(Link)``;
const StyledContent = styled(ParsedString)`
  padding: 0;
  font-size: inherit;
  line-height: 1.65;
  cursor: pointer;

  @media (max-width: ${style.collapse}px) {
    font-size: 0.875rem;
    line-height: 1.6;
  }
`;
const StyledHeader = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  font-size: 1rem;
  margin-bottom: 0.25rem;
  padding: 0;
  line-height: 1.4;

  & > ${Avatar} {
    flex: 0 0 auto;
    width: 2.5rem;
    height: 2.5rem;
    margin-right: 0.5rem;
  }

  h4 {
    margin: 0;
    flex-grow: 1;
    font-size: inherit;
    display: flex;
    flex-flow: column nowrap;
    font-size: 0.875rem;

    strong {
      font-weight: 700;
      font-size: inherit;
      vertical-align: baseline;

      a {
        margin-left: 0.25rem;
        text-decoration: underline;
        font-weight: 500;
        line-height: inherit;
      }
    }

    em {
      font-style: normal;
      font-weight: normal;
      color: ${style.black500};
      margin-left: 0;
      margin-top: 0.25rem;
      font-size: 0.875rem;
    }

    ${StyledGroupLink} {
      display: block;
      font-size: 0.875rem;
      line-height: 1.4;
      font-weight: normal;
      margin-top: 0.25rem;

      @media (max-width: ${style.collapse}px) {
        display: none;
      }
    }
  }

  ${StyledAction} {
    & > * {
      margin-left: 0.5rem;
    }

    ${RawFeatherIcon} {
      width: 1rem;
      height: 1rem;

      svg {
        width: inherit;
        height: inherit;
        stroke-width: 2;
      }
    }
  }
`;
const StyledCommentCount = styled.p`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: center;
  color: ${style.primary500};
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;

  @media (max-width: ${style.collapse}px) {
    justify-content: flex-start;
  }

  ${RawFeatherIcon} {
    width: 1rem;
    height: 1rem;
  }
`;
const StyledNewComment = styled.div``;
const StyledComments = styled.div`
  display: flex;
  flex-flow: column nowrap;
  justify-content: flex-start;

  @media (min-width: ${style.collapse}px) {
    border-top: 1px solid ${style.black100};
    transform: translateY(0.5rem);
    padding-top: 1.5rem;

    &:empty {
      border-top: none;
      transform: none;
    }
  }

  ${StyledNewComment} {
    margin-top: auto;
    padding: 1rem 0 0;

    &:first-child,
    &:empty {
      padding-top: 0;
    }
  }
`;
const StyledMessage = styled.div``;
const StyledWrapper = styled.div`
  width: 100%;
  padding: 1.5rem;
  margin: 0;
  background-color: white;
  scroll-margin-top: 160px;
  border: 1px solid ${style.black100};

  @media (max-width: ${style.collapse}px) {
    scroll-margin-top: 120px;
    border: none;
    padding: 1.5rem 1rem;
    box-shadow: ${style.elaborateShadow};
  }

  & + & {
    margin-top: 1.5rem;

    @media (max-width: ${style.collapse}px) {
      padding-top: 1.5rem;
      margin-top: 1rem;
    }
  }

  ${StyledMessage} {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    justify-content: flex-start;
    min-height: 100%;

    & > * {
      margin-top: 1rem;
      margin-bottom: 0;

      &:first-child,
      &:empty {
        margin-top: 0;
      }
    }

    ${StyledContent} {
      margin-top: 0.5rem;
    }

    ${Card} {
      @media (max-width: ${style.collapse}px) {
        box-shadow: none;
        border: 1px solid ${style.black100};
      }
    }

    ${StyledComments} {
      flex: 1 1 auto;

      &::before {
        @media (max-width: 580px) {
          display: ${({ $withMobileCommentField }) =>
            $withMobileCommentField ? "block" : "none"};
          content: "";
          padding: 0;
          width: 100%;
          height: 9px;
          background-color: ${style.black50};
          box-shadow: 0 1px 0 ${style.black200} inset;
          margin: 0 -1rem 1rem;
          box-sizing: content-box;
          padding: 0 1rem;
        }
      }
    }
  }
`;

const MessageCard = (props) => {
  const {
    user,
    message,
    groupURL,
    comments,
    isManager,
    isLoading,
    onClick,
    onComment,
    onReportComment,
    onDeleteComment,
    onDelete,
    onEdit,
    onReport,
    withMobileCommentField,
    scrollIn,
    withBottomButton,
  } = props;

  const { group, author, text, created, linkedEvent, commentCount } = message;

  const messageCardRef = useRef();

  const event = useMemo(() => formatEvent(linkedEvent), [linkedEvent]);

  const isAuthor = author.id === user.id;
  const canEdit = typeof onEdit === "function";
  const canDelete = typeof onDelete === "function";
  const canReport = typeof onReport === "function" && !isAuthor;
  const hasActions = canDelete || canReport;

  const messageURL = useMemo(() => {
    if (props.messageURL) {
      const url =
        window &&
        window.location &&
        window.location.origin &&
        !props.messageURL.includes("http")
          ? window.location.origin + props.messageURL
          : props.messageURL;

      return url;
    }
  }, [props.messageURL]);
  const encodedMessageURL = useMemo(
    () => messageURL && encodeURIComponent(messageURL),
    [messageURL]
  );
  const [isURLCopied, copyURL] = useCopyToClipboard(messageURL);

  const handleClick = useCallback(() => {
    onClick && onClick(message);
  }, [message, onClick]);
  const handleEdit = useCallback(() => {
    onEdit && onEdit(message);
  }, [message, onEdit]);
  const handleDelete = useCallback(() => {
    onDelete && onDelete(message);
  }, [message, onDelete]);
  const handleReport = useCallback(() => {
    onReport && onReport(message);
  }, [message, onReport]);
  const handleComment = useCallback(
    (comment) => {
      onComment && onComment(comment, message);
    },
    [message, onComment]
  );
  const handleDeleteComment = useCallback(
    (comment) => {
      onDeleteComment && onDeleteComment(comment, message);
    },
    [message, onDeleteComment]
  );
  const handleReportComment = useCallback(
    (comment) => {
      onReportComment && onReportComment(comment, message);
    },
    [message, onReportComment]
  );

  useEffect(() => {
    scrollIn &&
      messageCardRef.current &&
      messageCardRef.current.scrollIntoView &&
      messageCardRef.current.scrollIntoView();
  }, [scrollIn]);

  return (
    <StyledWrapper
      ref={messageCardRef}
      $withMobileCommentField={withMobileCommentField}
    >
      <StyledMessage>
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
            <em onClick={handleClick} style={{ cursor: "pointer" }}>
              {created ? timeAgo(created) : null}
            </em>
            {groupURL && group && group.name ? (
              <StyledGroupLink to={groupURL}>{group.name}</StyledGroupLink>
            ) : null}
          </h4>
          <StyledAction>
            {encodedMessageURL ? (
              <InlineMenu triggerIconName="share-2" triggerSize="1rem">
                <StyledInlineMenuItems>
                  <span>Partager avec d’autres membres du groupe&nbsp;:</span>
                  <a href={`https://t.me/share/url?url=${encodedMessageURL}`}>
                    <FaTelegram color={style.primary500} />
                    Telegram
                  </a>
                  <a href={`https://wa.me/?text=${encodedMessageURL}`}>
                    <FaWhatsapp color={style.primary500} />
                    Whatsapp
                  </a>
                  <button onClick={copyURL}>
                    <RawFeatherIcon
                      name={isURLCopied ? "check" : "copy"}
                      color={style.primary500}
                    />
                    {isURLCopied ? "Lien copié" : "Copier le lien"}
                  </button>
                </StyledInlineMenuItems>
              </InlineMenu>
            ) : null}
            {hasActions ? (
              <InlineMenu
                triggerIconName="more-horizontal"
                triggerSize="1rem"
                shouldDismissOnClick
              >
                <StyledInlineMenuItems>
                  {canEdit && (
                    <button onClick={handleEdit} disabled={isLoading}>
                      <RawFeatherIcon name="edit-2" color={style.primary500} />
                      Modifier
                    </button>
                  )}
                  {canDelete && (
                    <button onClick={handleDelete} disabled={isLoading}>
                      <RawFeatherIcon name="x" color={style.primary500} />
                      Supprimer
                    </button>
                  )}
                  {canReport && (
                    <button onClick={handleReport} disabled={isLoading}>
                      <RawFeatherIcon name="flag" color={style.primary500} />
                      Signaler
                    </button>
                  )}
                </StyledInlineMenuItems>
              </InlineMenu>
            ) : null}
          </StyledAction>
        </StyledHeader>
        <StyledContent onClick={handleClick}>{text}</StyledContent>
        {event ? <EventCard {...event} /> : null}
        {commentCount ? (
          <StyledCommentCount onClick={handleClick}>
            <RawFeatherIcon name="message-circle" color={style.primary500} />
            &ensp;Voir les {commentCount} commentaires
          </StyledCommentCount>
        ) : null}
        <StyledComments>
          <PageFadeIn ready={Array.isArray(comments) && comments.length > 0}>
            {Array.isArray(comments) && comments.length > 0
              ? comments.map((comment) => (
                  <Comment
                    key={comment.id}
                    comment={comment}
                    onDelete={onDeleteComment ? handleDeleteComment : undefined}
                    onReport={onReportComment ? handleReportComment : undefined}
                    isAuthor={comment.author.id === user.id}
                    isManager={isManager}
                  />
                ))
              : null}
          </PageFadeIn>
          <StyledNewComment>
            {onComment ? (
              withMobileCommentField ? (
                <CommentField
                  isLoading={isLoading}
                  user={user}
                  onSend={handleComment}
                />
              ) : (
                <ResponsiveLayout
                  MobileLayout={CommentButton}
                  DesktopLayout={CommentField}
                  isLoading={isLoading}
                  user={user}
                  onSend={handleComment}
                  onClick={onClick && handleClick}
                />
              )
            ) : null}
          </StyledNewComment>
        </StyledComments>
        {withBottomButton && (
          <div style={{ textAlign: "center" }}>
            <Button small onClick={handleClick}>
              Rejoindre la conversation
            </Button>
          </div>
        )}
      </StyledMessage>
    </StyledWrapper>
  );
};
MessageCard.propTypes = {
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
    commentCount: PropTypes.number,
  }).isRequired,
  messageURL: PropTypes.string,
  groupURL: PropTypes.string,
  comments: PropTypes.arrayOf(PropTypes.object),
  onClick: PropTypes.func,
  onComment: PropTypes.func,
  onDelete: PropTypes.func,
  onDeleteComment: PropTypes.func,
  onReportComment: PropTypes.func,
  onEdit: PropTypes.func,
  onReport: PropTypes.func,
  isLoading: PropTypes.bool,
  withMobileCommentField: PropTypes.bool,
  scrollIn: PropTypes.bool,
  isManager: PropTypes.bool,
  withBottomButton: PropTypes.bool,
};
export default MessageCard;
