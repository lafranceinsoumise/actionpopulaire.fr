import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

const StyledOnglets = styled("nav")`
  ul {
    display: flex;
    flex-direction: row;
    margin: 0;
    padding: 0 5px;
    justify-content: space-around;
  }

  li {
    flex: 1 1 auto;
    display: block;
    text-align: center;
    text-transform: uppercase;
    font-size: 12px;
    font-weight: 600;
    padding: 8px 0;
  }

  li.actif {
    border-bottom: 2px solid ${({ theme }) => theme.primary500};
  }

  li.actif a {
    color: ${({ theme }) => theme.primary500};
  }

  a {
    color: ${({ theme }) => theme.text1000};
    display: block;
    width: 100%;
    text-decoration: none;

    &:focus,
    &:hover {
      color: ${({ theme }) => theme.primary500};
    }
  }
`;

const Onglets = ({ onglets, actif, onChange }) => {
  return (
    <StyledOnglets>
      <ul>
        {Object.keys(onglets).map((k) => (
          <li key={k} className={k === actif ? "actif" : ""}>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                onChange(k);
              }}
            >
              {onglets[k]}
            </a>
          </li>
        ))}
      </ul>
    </StyledOnglets>
  );
};

Onglets.propTypes = {
  onglets: PropTypes.objectOf(PropTypes.string),
  actif: PropTypes.string,
  onChange: PropTypes.func,
};

export default Onglets;
