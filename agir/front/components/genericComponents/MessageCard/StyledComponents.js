import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import Avatar from "@agir/front/genericComponents/Avatar";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

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
export const StyledAction = styled.div`
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
export const StyledGroupLink = styled(Link)``;
export const StyledContent = styled.div`
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
export const StyledNewComment = styled.div``;
export const StyledComments = styled.div`
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
export const StyledPrivateVisibility = styled.div`
  padding: 20px;
  background-color: ${style.primary50};
  margin-bottom: 1rem;
  border-radius: ${style.borderRadius};
  display: flex;
  align-items: start;
`;
export const StyledLoadComments = styled.div`
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
