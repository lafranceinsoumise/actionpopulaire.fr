import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { formatEvent } from "@agir/events/common/utils";
import style from "@agir/front/genericComponents/_variables.scss";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";
import { timeAgo } from "@agir/lib/utils/time";
import { useCommentsSWR } from "@agir/msgs/common/hooks";
import { getMessageSubject } from "@agir/msgs/common/utils";

import Link from "@agir/front/app/Link";
import Comment from "@agir/front/formComponents/Comment";
import CommentField, {
  CommentButton,
} from "@agir/front/formComponents/CommentField";
import Avatar from "@agir/front/genericComponents/Avatar";
import EventCard from "@agir/front/genericComponents/EventCard";
import { FaTelegram, FaWhatsapp } from "@agir/front/genericComponents/FaIcon";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ParsedString from "@agir/front/genericComponents/ParsedString";
import {
  ResponsiveLayout,
  useIsDesktop,
} from "@agir/front/genericComponents/grid";
import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { StyledLoader } from "@agir/msgs/MessagePage/MessageThreadMenu";
import MessageAttachment from "../../formComponents/MessageAttachment";
import MessageHeader from "./MessageHeader";
import {
  StyledAction,
  StyledComments,
  StyledContent,
  StyledGroupLink,
  StyledHeader,
  StyledInlineMenuItems,
  StyledLoadComments,
  StyledMessage,
  StyledNewComment,
  StyledPrivateVisibility,
  StyledWrapper,
} from "./StyledComponents";

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
    autoScrollOnComment,
    commentErrors,
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
  } = useCommentsSWR(message.id, true);

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
    !message.readonly &&
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
                    errors={commentErrors}
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
                    errors={commentErrors}
                  />
                ))}
            </StyledNewComment>
          </StyledComments>
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
  autoScrollOnComment: PropTypes.bool,
  commentErrors: PropTypes.object,
};

export default MessageCard;
