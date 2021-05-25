import PropTypes from "prop-types";
import React, { useCallback } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import ParsedString from "@agir/front/genericComponents/ParsedString";

const StyledInlineMenuItems = styled.div`
  cursor: pointer;
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  list-style: none;
  color: ${style.primary500};
  padding: 0;
  margin: 0;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
  }

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

    ${RawFeatherIcon} {
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
const StyledMessageHeader = styled.header``;
const StyledMessageContent = styled.div``;
const StyledAction = styled.div``;
const StyledMessage = styled.div``;
const StyledWrapper = styled(animated.div)`
  display: flex;
  flex-flow: row nowrap;
  max-width: 100%;

  & + & {
    margin-top: 1rem;
  }

  ${Avatar} {
    flex: 0 0 auto;
    width: 2rem;
    height: 2rem;
    margin-top: 5px;
    margin-right: 0.5rem;
  }

  ${StyledMessage} {
    display: flex;
    border-radius: 8px;
    background-color: ${style.black50};
    flex-direction: row;
    padding: 0.75rem;
  }

  ${StyledMessageHeader} {
    font-size: 0.875rem;
    display: flex;
    flex-direction: row;
    align-items: baseline;

    @media (max-width: ${style.collapse}px) {
      flex-direction: column;
      align-items: flex-start;
    }

    strong {
      font-weight: 700;
      font-size: 0.875rem;

      a {
        margin-left: 0.25rem;
        text-decoration: underline;
        font-weight: 500;
        line-height: inherit;
      }
    }

    em {
      font-weight: normal;
      font-size: 13px;
      color: ${style.black700};
      margin-left: 0.5rem;
      font-style: normal;

      @media (max-width: ${style.collapse}px) {
        margin: 0.25rem 0;
      }
    }
  }

  ${StyledMessageContent} {
    font-size: 0.875rem;

    strong {
      font-weight: 600;
      font-size: inherit;
    }

    article {
      margin: 0;
      padding: 0;
      font-size: inherit;
      font-family: inherit;
      line-height: 1.65;
    }
  }

  ${StyledAction} {
    flex: 0 0 auto;
    margin-left: 1rem;
  }
`;

const Comment = (props) => {
  const { comment, onDelete, onReport, isAuthor, isManager } = props;
  const { author, text, created } = comment;

  const canDelete = typeof onDelete === "function" && (isAuthor || isManager);
  const canReport = typeof onReport === "function" && !isAuthor;
  const hasActions = canDelete || canReport;

  const transitions = useTransition(true, {
    from: { opacity: 0 },
    enter: { opacity: 1 },
    leave: { opacity: 0 },
    immediate: true,
  });

  const handleDelete = useCallback(() => {
    onDelete && onDelete(comment);
  }, [comment, onDelete]);

  const handleReport = useCallback(() => {
    onReport && onReport(comment);
  }, [comment, onReport]);

  return transitions((style) => (
    <StyledWrapper style={style}>
      <Avatar {...author} />
      <StyledMessage>
        <StyledMessageContent>
          <StyledMessageHeader>
            <strong>
              {author.displayName || (isAuthor && "Moi") || "Quelqu'un"}
              {!author.displayName && isAuthor && (
                <Link route="personalInformation">Ajouter mon nom</Link>
              )}
            </strong>
            <em>{created ? timeAgo(created) : null}</em>
          </StyledMessageHeader>
          <ParsedString as="article">{text}</ParsedString>
        </StyledMessageContent>
        {hasActions ? (
          <StyledAction>
            <InlineMenu
              triggerIconName="more-horizontal"
              triggerSize="1rem"
              shouldDismissOnClick
            >
              <StyledInlineMenuItems>
                {canDelete && (
                  <button onClick={handleDelete}>
                    <RawFeatherIcon name="x" color={style.primary500} />
                    Supprimer
                  </button>
                )}
                {canReport && (
                  <button onClick={handleReport}>
                    <RawFeatherIcon name="flag" color={style.primary500} />
                    Signaler
                  </button>
                )}
              </StyledInlineMenuItems>
            </InlineMenu>
          </StyledAction>
        ) : null}
      </StyledMessage>
    </StyledWrapper>
  ));
};
Comment.propTypes = {
  comment: PropTypes.shape({
    id: PropTypes.string.isRequired,
    author: PropTypes.shape({
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired,
    text: PropTypes.string.isRequired,
    created: PropTypes.string,
  }).isRequired,
  isAuthor: PropTypes.bool,
  onDelete: PropTypes.func,
  onReport: PropTypes.func,
};
export default Comment;
