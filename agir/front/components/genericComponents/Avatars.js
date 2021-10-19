import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Avatar from "./Avatar";

const StyledWrapper = styled.span`
  display: inline-block;
  padding: 0;
  margin: 0;
  line-height: 0;
  display: grid;
  grid-template-columns: 20px 20px 20px;
  grid-template-rows: 20px 20px 20px;
  isolation: isolate;

  ${Avatar} {
    width: 40px;
    height: 40px;
    border: 3px solid white;
    background-color: white;

    :first-child {
      grid-column: 1/3;
      grid-row: 1/3;
      z-index: 1;
    }

    :last-child {
      grid-column: 2/4;
      grid-row: 2/4;
    }
  }
`;

const Avatars = (props) => {
  const { people, ...rest } = props;

  if (!Array.isArray(people) || people.length === 0) {
    return null;
  }

  if (people.length === 1) {
    return (
      <Avatar
        {...rest}
        displayName={people[0].displayName}
        image={people[0].image}
      />
    );
  }

  return (
    <StyledWrapper {...rest}>
      {people.slice(0, 2).map((person, i) => (
        <Avatar
          key={person.id + i}
          displayName={person.displayName}
          image={person.image}
        />
      ))}
    </StyledWrapper>
  );
};
Avatars.propTypes = {
  people: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      displayName: PropTypes.string.isRequired,
      image: PropTypes.string,
    }).isRequired
  ).isRequired,
};
export default Avatars;
