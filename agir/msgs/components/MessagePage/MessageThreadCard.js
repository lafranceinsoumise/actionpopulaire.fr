import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { getMessageSubject } from "@agir/msgs/utils";
import { timeAgo } from "@agir/lib/utils/time";

import Avatar from "@agir/front/genericComponents/Avatar";
import Avatars from "@agir/front/genericComponents/Avatars";

const StyledUnreadItemBadge = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background-color: ${style.redNSP};
  text-align: center;
  border-radius: 100%;
  font-weight: 700;
  font-size: 0.813rem;
  line-height: 0;
  color: ${({ $empty }) => ($empty ? style.redNSP : style.white)};
  opacity: ${({ $empty }) => ($empty ? "0" : "1")};
  transform: scale(${({ $empty }) => ($empty ? "0" : "1")});
  transition: color, opacity, transform 150ms ease-out;
  will-change: color, opacity, transform;
`;

const StyledCard = styled.button`
  width: 100%;
  padding: 1rem;
  display: flex;
  text-align: left;
  justify-content: space-between;
  align-items: center;
  border: none;
  cursor: pointer;
  background-color: ${({ $selected }) =>
    $selected ? style.black50 : style.white};
  box-shadow: inset ${({ $selected }) => ($selected ? "2px" : "0px")} 0px 0px
    ${style.primary500};

  &[disabled] {
    cursor: default;
  }

  & > * {
    flex: 0 0 auto;
  }

  & > ${Avatar} {
    width: 50px;
    height: 50px;
    margin-right: 8px;
  }

  & > article {
    flex: 1 1 auto;
    margin: 0 18px 0 12px;
    min-width: 0;
    color: ${style.black700};

    h6,
    h5,
    p {
      margin: 0 0 0.25rem;
      padding: 0;
      display: block;
      font-weight: 400;
      font-size: 0.875rem;
    }

    h6,
    h5,
    p span {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    h6 {
      color: ${(props) => props.theme.primary500};
    }

    h5 {
      font-size: 1rem;
      font-weight: 500;
      color: ${style.black1000};
    }

    p {
      display: flex;
      justify-content: flex-start;

      & > * {
        flex: 0 0 auto;
        margin: 0;

        :first-child {
          flex: 0 1 auto;
        }
      }
    }
  }
`;

const MessageThreadCard = (props) => {
  const { message, isLoading, isSelected, onClick } = props;

  const {
    id,
    author,
    group,
    isUnread,
    unreadCommentCount,
    lastComment,
    lastUpdate,
  } = message;

  const handleClick = useCallback(() => {
    onClick && onClick(id);
  }, [onClick, id]);

  const unreadItemCount = (isUnread ? 1 : 0) + (unreadCommentCount || 0);
  const subject = getMessageSubject(message);
  const time = timeAgo(lastUpdate).replace("il y a", "");
  const text = lastComment
    ? `${lastComment.author.displayName} : ${lastComment.text}`
    : `${message.author.displayName} : ${message.text}`;
  const authors =
    author.id && lastComment?.author && lastComment.author.id !== author.id
      ? [author, lastComment.author]
      : [author];

  return (
    <StyledCard
      type="button"
      onClick={handleClick}
      $selected={isSelected}
      disabled={isLoading}
    >
      <Avatars people={authors} />
      <article>
        <h6 title={group.name}>{group.name}</h6>
        <h5 title={subject}>{subject}</h5>
        <p title={text}>
          <span>{text}</span>
          <span>&nbsp;•&nbsp;{time}</span>
        </p>
      </article>
      <StyledUnreadItemBadge
        aria-label="Nombre de commentaires non lus"
        $empty={unreadItemCount === 0}
      >
        {unreadItemCount}
      </StyledUnreadItemBadge>
    </StyledCard>
  );
};

MessageThreadCard.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    created: PropTypes.string.isRequired,
    subject: PropTypes.string,
    author: PropTypes.shape({
      id: PropTypes.string,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    group: PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    }).isRequired,
    text: PropTypes.string.isRequired,
    lastUpdate: PropTypes.string.isRequired,
    lastComment: PropTypes.shape({
      id: PropTypes.string.isRequired,
      created: PropTypes.string.isRequired,
      author: PropTypes.shape({
        id: PropTypes.string,
        displayName: PropTypes.string.isRequired,
        image: PropTypes.string,
      }).isRequired,
      text: PropTypes.string.isRequired,
    }),
    unreadCommentCount: PropTypes.number,
    isUnread: PropTypes.bool,
  }).isRequired,
  isLoading: PropTypes.bool,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func,
};

export default MessageThreadCard;
