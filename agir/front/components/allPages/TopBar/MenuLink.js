import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Link from "@agir/front/app/Link";
import Avatar from "@agir/front/genericComponents/Avatar";

const MenuLink = styled(Link)`
  display: flex;
  align-items: center;
  color: ${style.black1000};
  font-weight: 500;
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

export default MenuLink;
