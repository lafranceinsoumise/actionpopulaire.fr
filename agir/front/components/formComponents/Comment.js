import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import { animated, useTransition } from "react-spring";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";

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
    flex: 1 1 auto;
    border-radius: 8px;
    background-color: ${style.black50};
    flex-flow: row nowrap;
    padding: 0.75rem;
  }

  ${StyledMessageHeader} {
    font-size: 0.875rem;
    display: flex;
    flex-direction: row;

    @media (max-width: ${style.collapse}px) {
      flex-direction: column;
    }

    strong {
      font-weight: 600;
      font-size: inherit;
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
    flex: 1 1 auto;
    font-size: 0.875rem;

    strong {
      font-weight: 600;
      font-size: inherit;
    }

    article {
      flex: 1 1 auto;
      margin: 0;
      padding: 0;
      font-size: inherit;
      font-family: inherit;
      line-height: 1.65;

      span {
        display: block;
        min-height: 1em;
        font-size: inherit;
        line-height: inherit;
      }
    }
  }

  ${StyledAction} {
    flex: 0 0 auto;
  }
`;

const CommentField = (props) => {
  const { message, onDelete, onReport, isAuthor } = props;

  const { author, content, created } = message;

  const transitions = useTransition(true, null, {
    from: { opacity: 0 },
    enter: { opacity: 1 },
    leave: { opacity: 0 },
    immediate: true,
  });

  const hasActions = useMemo(
    () =>
      isAuthor
        ? typeof onDelete === "function"
        : typeof onReport === "function",
    [isAuthor, onDelete, onReport]
  );

  const handleDelete = useCallback(() => {
    onDelete && onDelete(message);
  }, [message, onDelete]);

  const handleReport = useCallback(() => {
    onReport && onReport(message);
  }, [message, onReport]);

  return transitions.map(({ key, props }) => (
    <StyledWrapper key={key} style={props}>
      <Avatar {...author} />
      <StyledMessage>
        <StyledMessageContent>
          <StyledMessageHeader>
            <strong>{author.fullName}</strong>
            <em>{created ? timeAgo(created) : null}</em>
          </StyledMessageHeader>
          <article>
            {content.split("\n").map((paragraph, i) => (
              <span key={i + "__" + paragraph}>{paragraph}</span>
            ))}
          </article>
        </StyledMessageContent>
        {hasActions ? (
          <StyledAction>
            <InlineMenu triggerIconName="more-horizontal" triggerSize="1rem">
              <StyledInlineMenuItems>
                {isAuthor && onDelete && (
                  <button onClick={handleDelete}>
                    <RawFeatherIcon name="x" color={style.primary500} />
                    Supprimer
                  </button>
                )}
                {!isAuthor && onReport && (
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
CommentField.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string,
    author: PropTypes.shape({
      fullName: PropTypes.string.isRequired,
      avatar: PropTypes.string,
    }).isRequired,
    content: PropTypes.string.isRequired,
    created: PropTypes.string,
  }).isRequired,
  isAuthor: PropTypes.bool,
  onDelete: PropTypes.func,
  onReport: PropTypes.func,
};
export default CommentField;
