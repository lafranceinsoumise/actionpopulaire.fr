import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { InfosElu } from "@agir/elus/parrainages/types";
import { StatutPill } from "../types";

const SelecteurElusLayout = styled.ul`
  display: block;
  margin: 0;
  padding: 0;
  background-color: ${(props) => props.theme.text25};

  li {
  }

  li + li {
    border-top: 1px solid ${(props) => props.theme.text50};
  }

  strong {
    font-size: 1rem;
    font-weight: 600;
  }
`;

const Button = styled.button`
  width: 100%;

  background-color: ${(props) => props.theme.text25};
  border: 0;
  margin: 0;
  padding: 1rem;
  border-left: 3px solid
    ${(props) => (props.selected ? props.theme.primary500 : props.theme.text25)};
  cursor: pointer;

  text-align: left;

  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SelecteurElus = ({ elus, onSelect, selected }) => {
  return (
    <SelecteurElusLayout>
      {elus.map((elu) => (
        <li key={elu.id}>
          <Button selected={elu === selected} onClick={() => onSelect(elu)}>
            <div>
              <strong>{elu.nomComplet}</strong>
              <br />
              {elu.commune}
            </div>
            <StatutPill statut={elu.statut} />
          </Button>
        </li>
      ))}
    </SelecteurElusLayout>
  );
};

SelecteurElus.propTypes = {
  elus: PropTypes.arrayOf(InfosElu),
  onSelect: PropTypes.func,
  selected: InfosElu,
};
SelecteurElus.defaultProps = {
  elus: [],
  onSelect: () => {},
};
SelecteurElus.Layout = SelecteurElusLayout;

export default SelecteurElus;
