import PropTypes from "prop-types";
import React, { useCallback } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";
import { timeAgo } from "@agir/lib/utils/time";

import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import ParsedString from "@agir/front/genericComponents/ParsedString";
import MessageAttachment from "./MessageAttachment";

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
const StyledMessageAuthor = styled.h5``;
const StyledMessageContent = styled.div``;
const StyledMessageTime = styled.div``;
const StyledAction = styled.div``;
const StyledMessage = styled.div``;
const StyledWrapper = styled(animated.div)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  max-width: 100%;
  padding: 1rem 0;
  border-top: 1px solid ${(props) => props.theme.black100};

  &:first-child {
    border-top: none;
  }

  ${Avatar} {
    flex: 0 0 auto;
    width: 2rem;
    height: 2rem;
    margin-right: 0.5rem;
  }

  ${StyledMessage} {
    display: flex;
    flex: 1 1 auto;
    border-radius: ${style.borderRadius};
    flex-direction: column;
  }

  ${StyledMessageHeader} {
    display: flex;
    flex-flow: row nowrap;
    align-items: flex-start;
    line-height: 1.5;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;

    ${StyledMessageAuthor} {
      flex: 1 1 auto;
      padding: 0;
      margin: 0;
      font-weight: 700;
    }

    ${StyledMessageTime} {
      padding-left: 1rem;
      flex: 0 0 auto;
      font-size: 0.813rem;
      color: ${style.black700};
      font-style: normal;
    }

    ${StyledAction} {
      flex: 0 0 auto;
      padding-left: 1rem;
      height: 18px;
    }
  }

  ${StyledMessageContent} {
    flex: 1 1 auto;
    font-size: 0.875rem;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;

    article {
      margin: 0;
      padding: 0;
      font-size: inherit;
      font-family: inherit;
      line-height: 1.65;

      &:empty {
        display: none;
      }
    }
  }
`;

const Comment = (props) => {
  const { comment, onDelete, onReport, isAuthor, isManager } = props;
  const { author, text, attachment, created } = comment;

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
        <StyledMessageHeader>
          <StyledMessageAuthor>
            {author.displayName || (isAuthor && "Moi") || "Quelqu'un"}
          </StyledMessageAuthor>
          <StyledMessageTime>
            {created ? timeAgo(created) : null}
          </StyledMessageTime>
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
        </StyledMessageHeader>
        <StyledMessageContent>
          <ParsedString as="article">{text}</ParsedString>
          <MessageAttachment file={attachment?.file} name={attachment?.name} />
        </StyledMessageContent>
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
    attachment: PropTypes.shape({
      name: PropTypes.string,
      file: PropTypes.string,
    }),
    created: PropTypes.string,
  }).isRequired,
  isAuthor: PropTypes.bool,
  onDelete: PropTypes.func,
  onReport: PropTypes.func,
};
export default Comment;
