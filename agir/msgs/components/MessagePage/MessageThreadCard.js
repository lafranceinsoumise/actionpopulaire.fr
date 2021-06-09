import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Avatar from "@agir/front/genericComponents/Avatar";

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

  ${Avatar} {
    width: 2.5rem;
    height: 2.5rem;
  }

  & > article {
    flex: 1 1 auto;
    margin: 0 12px;
    min-width: 0;

    h5,
    p {
      font-weight: 400;
      font-size: 0.875rem;
      color: ${style.black700};
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin: 0;
    }

    h5 strong {
      font-weight: inherit;
      font-size: 1rem;
      color: ${style.black1000};
    }
  }
`;

const MessageThreadCard = (props) => {
  const {
    message: { id, author, group, text, isUnread, unreadCommentCount },
    isLoading,
    isSelected,
    onClick,
  } = props;

  const handleClick = useCallback(() => {
    onClick && onClick(id);
  }, [onClick, id]);

  const unreadItemCount = (isUnread ? 1 : 0) + (unreadCommentCount || 0);

  return (
    <StyledCard
      type="button"
      onClick={handleClick}
      $selected={isSelected}
      disabled={isLoading}
    >
      <Avatar name={author?.displayName} image={author?.image} />
      <article>
        <h5 title={`${author?.displayName} • ${group?.name}`}>
          <strong>{author?.displayName}</strong>&nbsp;•&nbsp;{group?.name}
        </h5>
        <p title={text}>{text}</p>
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
    author: PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    group: PropTypes.shape({
      name: PropTypes.string.isRequired,
    }).isRequired,
    text: PropTypes.string.isRequired,
    unreadCommentCount: PropTypes.number,
    isUnread: PropTypes.bool,
  }).isRequired,
  isLoading: PropTypes.bool,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func,
};

export default MessageThreadCard;
