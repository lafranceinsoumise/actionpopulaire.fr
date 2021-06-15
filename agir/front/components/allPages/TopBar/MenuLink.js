import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import Avatar from "@agir/front/genericComponents/Avatar";

const MenuLink = styled(Link)`
  display: flex;
  align-items: center;
  color: ${style.black1000};
  font-weight: 400;
  height: 3rem;
  border: none;
  background-color: transparent;
  cursor: pointer;

  * + * {
    margin-left: 0.5em;
  }

  :hover {
    outline: none;
    text-decoration: none;
    color: ${style.black1000};

    & > * {
      text-decoration: underline;
    }

    & > div {
      text-decoration: none;
    }
  }

  @media (max-width: ${style.collapse}px) {
    height: 1.5rem;
  }

  ${Avatar} {
    height: 2.5rem;
    width: 2.5rem;

    @media (max-width: ${style.collapse}px) {
      height: 2rem;
      width: 2rem;
    }
  }
`;

export const TopbarLink = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 72px;
  padding-left: 11px;
  padding-right: 11px;
  transition: 0.2s ease;
  font-size: 12px;
  position: relative;
  color: ${({ $active }) => ($active ? style.primary500 : "")};

  span {
    margin: 0;
    margin-top: 5px;
    max-width: 75px;
    text-overflow: ellipsis;
    overflow: hidden;
    word-wrap: initial;
    white-space: nowrap;
  }

  &:hover {
    color: ${style.primary500};
  }

  div {
    display: ${({ $active }) => ($active ? "block" : "none")};
    position: absolute;
    bottom: 0px;
    right: 0px;
    width: 100%;
    height: 2px;
    background-color: ${style.primary500};
  }

  small {
    display: flex;
    color: ${style.white};
    position: absolute;
    background-color: ${style.redNSP};
    font-weight: 700;
    font-size: 11px;
    border-radius: 100%;
    align-items: center;
    justify-content: center;
    top: 10px;
    right: 20px;
    width: 18px;
    height: 18px;
    overflow: hidden;
    white-space: nowrap;

    &:empty {
      top: 12px;
      right: 30px;
      width: 0.5rem;
      height: 0.5rem;
    }
  }
`;

export default MenuLink;
