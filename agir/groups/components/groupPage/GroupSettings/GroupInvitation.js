import PropTypes from "prop-types";
import React, { useState } from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { Column, Row } from "@agir/front/genericComponents/grid";

const StyledInput = styled.input`
  min-width: 240px;
  width: 100%;
  height: 2rem;
  border: 1px solid ${style.black100};
  border-radius: 0.5rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
`;

const StyledDiv = styled.div`
  font-weight: 500;
`;

const GroupInvitation = (props) => {
  const { title } = props;

  const [email, setEmail] = useState("");

  const handleChange = (e) => {
    setEmail(e.target.value);
  };

  const handleInvitation = (e) => {
    console.log("invite : ", email);
    setEmail("");
  };

  return (
    <StyledDiv>
      <Row gutter={2} style={{ marginBottom: "1rem" }}>
        <Column grow collapse={false}>
          {title}
        </Column>
      </Row>

      <Row gutter={4}>
        <Column grow collapse={false}>
          {" "}
          <StyledInput
            type="text"
            value={email}
            placeholder="Adresse e-mail de l’invité·e"
            onChange={handleChange}
          />
        </Column>
        <Column collapse={false}>
          <Button color="primary" small onClick={handleInvitation}>
            Envoyer une invitation
          </Button>
        </Column>
      </Row>
    </StyledDiv>
  );
};
GroupInvitation.propTypes = {
  title: PropTypes.string,
};
export default GroupInvitation;
