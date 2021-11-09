import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Avatars from "@agir/front/genericComponents/Avatars";

import { StyledCard } from "./styledComponents";

const StyledH5 = styled.h5`
  && {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    max-height: 40px;
    overflow: hidden;
    white-space: normal;
  }
`;

const MessageThreadCardOrganization = ({ group }) => {
  const subject = (
    <>
      Entrez en contact avec {group.referents[0].displayName}
      {group.referents.length > 1 && (
        <>&nbsp;et {group.referents[1].displayName}</>
      )}
      &nbsp;!
    </>
  );

  return (
    <StyledCard type="button" $selected={true}>
      <Avatars people={group.referents} />
      <article>
        <h6 title={group.name}>{group.name}</h6>
        <StyledH5 title={subject}>{subject}</StyledH5>
      </article>
    </StyledCard>
  );
};

export default MessageThreadCardOrganization;
