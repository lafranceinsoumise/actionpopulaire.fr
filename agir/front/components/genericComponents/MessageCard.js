import PropTypes from "prop-types";
import React, {
  useCallback,
  useState,
  useEffect,
  useMemo,
  useRef,
} from "react";

import styled from "styled-components";

import { FaWhatsapp, FaTelegram } from "@agir/front/genericComponents/FaIcon";

import style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";
import { formatEvent } from "@agir/events/common/utils";
import { getMessageSubject } from "@agir/msgs/common/utils";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";
import MessageDetails from "@agir/front/genericComponents/MessageDetails";

import Spacer from "@agir/front/genericComponents/Spacer";
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
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import ButtonMuteMessage from "./ButtonMuteMessage";
import ButtonLockMessage from "./ButtonLockMessage";
import ModalConfirmation from "@agir/front/genericComponents/ModalConfirmation";

import { useCommentsSWR } from "@agir/msgs/common/hooks";
import { StyledLoader } from "@agir/msgs/MessagePage/MessageThreadMenu";
import MessageAttachment from "../formComponents/MessageAttachment";

export const StyledInlineMenuItems = styled.div`
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
      font-size: 1rem;

      @media (max-width: ${style.collapse}px) {
        margin-right: 1rem;
        width: 1.5rem;
        height: 1.5rem;
        font-size: 1.5rem;
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
const StyledContent = styled.div`
  padding: 0;
  font-size: inherit;
  line-height: 1.65;

  @media (max-width: ${style.collapse}px) {
    font-size: 0.875rem;
    line-height: 1.6;
  }

  & > p:last-of-type {
    margin-bottom: 0;
  }
`;
export const StyledHeader = styled.div`
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
const StyledNewComment = styled.div``;
const StyledComments = styled.div`
  display: flex;
  flex-flow: column nowrap;
  justify-content: flex-start;

  @media (min-width: ${style.collapse}px) {
    border-top: ${({ $empty }) =>
      $empty ? "none" : `1px solid ${style.black100}`};
    transform: ${({ $empty }) => ($empty ? "none" : "translateY(0.5rem)")};
  }

  ${StyledNewComment} {
    margin-top: auto;
    padding: 1rem 0 0;

    &:empty {
      display: none;
    }

    &:first-child {
      padding-top: 0;
    }
  }
`;
export const StyledSubject = styled.h2`
  font-size: 1.125rem;
  line-height: 1.5;
  font-weight: 600;
  margin: 0;
  display: inline-flex;
  align-items: center;

  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  cursor: pointer;

  @media (max-width: ${style.collapse}px) {
    white-space: normal;
    cursor: default;
  }

  @media (min-width: ${style.collapse}px) {
    max-width: 360px;
  }
  @media (min-width: 1300px) {
    max-width: 560px;
  }

  ${RawFeatherIcon} {
    background-color: #eeeeee;
    border-radius: 2rem;
    padding: 8px;
    margin-right: 0.5rem;
  }
`;
export const StyledMessage = styled.div``;
export const StyledWrapper = styled.div`
  width: 100%;
  padding: 1.5rem;
  margin: 0;
  background-color: white;
  scroll-margin-top: 160px;
  border: 1px solid ${style.black100};
  overflow-x: hidden;
  height: calc(100% - 80px);

  @media (max-width: ${style.collapse}px) {
    scroll-margin-top: 120px;
    padding: 1.5rem 1rem;
    box-shadow: ${style.elaborateShadow};
  }

  ${StyledMessage} {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    justify-content: flex-start;

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

const StyledPrivateVisibility = styled.div`
  padding: 20px;
  background-color: ${style.primary50};
  margin-bottom: 1rem;
  border-radius: ${style.borderRadius};
  display: flex;
  align-items: start;
`;

const StyledMessageHeader = styled.div`
  height: 80px;
  padding: 1rem;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border: 1px solid #dfdfdf;
  border-bottom: none;
  background-color: white;

  @media (max-width: ${style.collapse}px) {
    padding: 0;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    height: unset;
    border: none;
  }
`;

const StyledLoadComments = styled.div`
  display: flex;
  align-items: center;
  justify-content: left;
  padding: 10px;
  cursor: pointer;
  color: ${style.primary500};

  ${RawFeatherIcon} {
    margin-right: 0.5rem;
  }
`;

const MessageHeader = ({ message, subject, isManager, isAuthor }) => {
  const isDesktop = useIsDesktop();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const showModal = () => {
    if (!isDesktop) {
      return;
    }
    setIsModalOpen(true);
  };

  return (
    <>
      <StyledMessageHeader>
        <div style={{ display: "flex" }}>
          {isDesktop && (
            <RawFeatherIcon name="mail" style={{ marginRight: "1rem" }} />
          )}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
            }}
          >
            <StyledSubject onClick={showModal}>{subject}</StyledSubject>
            <MessageDetails message={message} />
          </div>
        </div>
        {!message?.readonly && isDesktop && (
          <div>
            {(isManager || isAuthor) && <ButtonLockMessage message={message} />}
            <Spacer size="0.5rem" style={{ display: "inline-block" }} />
            {<ButtonMuteMessage message={message} />}
          </div>
        )}
      </StyledMessageHeader>
      <ModalConfirmation
        shouldShow={isModalOpen}
        shouldDismissOnClick={false}
        onClose={() => setIsModalOpen(false)}
      >
        <h3>{subject}</h3>
      </ModalConfirmation>
    </>
  );
};
MessageHeader.propTypes = {
  message: PropTypes.shape({
    text: PropTypes.string.isRequired,
    readonly: PropTypes.bool,
  }),
  subject: PropTypes.string.isRequired,
  isManager: PropTypes.bool,
  isAuthor: PropTypes.bool,
};

const MessageCard = (props) => {
  const {
    user,
    message,
    groupURL,
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
    withBottomButton,
    autoScrollOnComment,
  } = props;

  const {
    group,
    author,
    text,
    created,
    linkedEvent,
    lastUpdate,
    attachment,
    isLocked,
    readonly,
  } = message;

  const {
    comments,
    commentsCount,
    loadMore: loadMoreComments,
    isLoadingMore: isLoadingComments,
    mutate: mutateComments,
  } = useCommentsSWR(message.id);

  const messageCardRef = useRef();
  const isDesktop = useIsDesktop();

  const [loadedComments, setLoadedComments] = useState(false);
  const event = useMemo(() => formatEvent(linkedEvent), [linkedEvent]);

  const isAuthor = author.id === user.id;
  const canEdit = !readonly && typeof onEdit === "function";
  const canDelete = !readonly && typeof onDelete === "function";
  const canReport = !readonly && typeof onReport === "function" && !isAuthor;
  const hasActions = canEdit || canDelete || canReport;

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
    [messageURL],
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
    [message, onComment],
  );
  const handleDeleteComment = useCallback(
    (comment) => {
      onDeleteComment && onDeleteComment(comment, message);
    },
    [message, onDeleteComment],
  );
  const handleReportComment = useCallback(
    (comment) => {
      onReportComment && onReportComment(comment, message);
    },
    [message, onReportComment],
  );

  useEffect(() => {
    if (messageCardRef && !loadedComments) {
      messageCardRef.current.scrollTo(0, messageCardRef.current.scrollHeight);
      setLoadedComments(true);
    }
  }, [loadedComments]);

  useEffect(() => {
    lastUpdate && mutateComments && mutateComments();
  }, [lastUpdate, mutateComments]);

  const isOrganizerMessage =
    message.requiredMembershipType > MEMBERSHIP_TYPES.MEMBER;

  let subject = getMessageSubject(message);
  if (isOrganizerMessage && !subject) {
    subject = `Message privé avec les animateur⋅ices de '${group.name}'`;
  }

  return (
    <>
      {isDesktop && (
        <MessageHeader
          subject={subject}
          message={message}
          isManager={isManager}
          isAuthor={isAuthor}
        />
      )}
      <StyledWrapper
        ref={messageCardRef}
        $withMobileCommentField={withMobileCommentField}
      >
        {!isDesktop && <MessageHeader subject={subject} message={message} />}

        <StyledMessage>
          {isOrganizerMessage && (
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
              <em onClick={handleClick} style={{ cursor: "pointer" }}>
                {created ? timeAgo(created) : null}
              </em>
              {groupURL && group && group.name ? (
                <StyledGroupLink to={groupURL}>{group.name}</StyledGroupLink>
              ) : null}
            </h4>
            <StyledAction>
              {!!encodedMessageURL && (
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
              )}
              {hasActions && (
                <InlineMenu
                  triggerIconName="more-horizontal"
                  triggerSize="1rem"
                  shouldDismissOnClick
                >
                  <StyledInlineMenuItems>
                    {canEdit && (
                      <button onClick={handleEdit} disabled={isLoading}>
                        <RawFeatherIcon
                          name="edit-2"
                          color={style.primary500}
                        />
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
              )}
            </StyledAction>
          </StyledHeader>
          <StyledContent onClick={handleClick}>
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
                  onDelete={onDeleteComment ? handleDeleteComment : undefined}
                  onReport={onReportComment ? handleReportComment : undefined}
                  isAuthor={comment.author.id === user.id}
                  isManager={isManager}
                />
              ))}
            </PageFadeIn>
            <StyledNewComment>
              {!!onComment &&
                (withMobileCommentField ? (
                  <CommentField
                    id={message.id}
                    comments={comments}
                    isLoading={isLoading}
                    readonly={readonly}
                    isLocked={isLocked}
                    user={user}
                    onSend={handleComment}
                    autoScroll={autoScrollOnComment}
                    scrollerRef={messageCardRef}
                  />
                ) : (
                  <ResponsiveLayout
                    id={message.id}
                    comments={comments}
                    MobileLayout={CommentButton}
                    DesktopLayout={CommentField}
                    isLoading={isLoading}
                    readonly={readonly}
                    isLocked={isLocked}
                    user={user}
                    onSend={handleComment}
                    onClick={onClick && handleClick}
                    autoScroll={autoScrollOnComment}
                    scrollerRef={messageCardRef}
                  />
                ))}
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
    </>
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
    lastUpdate: PropTypes.string,
    attachment: PropTypes.shape({
      file: PropTypes.string,
      name: PropTypes.string,
    }),
    isLocked: PropTypes.bool,
    readonly: PropTypes.bool,
    requiredMembershipType: PropTypes.number,
  }).isRequired,
  messageURL: PropTypes.string,
  groupURL: PropTypes.string,
  onClick: PropTypes.func,
  onComment: PropTypes.func,
  onDelete: PropTypes.func,
  onDeleteComment: PropTypes.func,
  onReportComment: PropTypes.func,
  onEdit: PropTypes.func,
  onReport: PropTypes.func,
  isLoading: PropTypes.bool,
  withMobileCommentField: PropTypes.bool,
  isManager: PropTypes.bool,
  withBottomButton: PropTypes.bool,
  autoScrollOnComment: PropTypes.bool,
};
export default MessageCard;
