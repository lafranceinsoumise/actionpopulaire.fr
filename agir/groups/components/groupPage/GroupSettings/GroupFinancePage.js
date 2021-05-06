import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

import { getFinance } from "@agir/groups/groupPage/api.js";
import { useGroup } from "@agir/groups/groupPage/hooks/group.js";
import { useGroupWord } from "@agir/groups/utils/group";

const Buttons = styled.div`
  display: grid;
  grid-template-columns: auto auto;
  grid-gap: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    grid-template-columns: 1fr;
  }

  ${Button} {
    margin: 0;
    justify-content: center;
  }
`;

const GroupFinancePage = (props) => {
  const { onBack, illustration, groupPk } = props;

  const [donation, setDonation] = useState(0);

  const group = useGroup(groupPk);
  const withGroupWord = useGroupWord(group);

  const getFinanceAPI = useCallback(async (groupPk) => {
    const res = await getFinance(groupPk);
    setDonation(res.data.donation);
  }, []);

  useEffect(() => {
    groupPk && getFinanceAPI(groupPk);
  }, [groupPk, getFinanceAPI]);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      <StyledTitle>
        {withGroupWord`Dons alloués aux personnes de mon groupe`}
      </StyledTitle>

      <Spacer size="1rem" />

      <span style={{ fontSize: "2rem" }}>{donation} €</span>

      <Spacer size="1rem" />

      <div style={{ color: style.black700 }}>
        {!donation && (
          <>
            Personne n'a encore alloué de dons à vos actions.
            <br />
          </>
        )}
        Vous pouvez allouer des dons à vos actions sur la{" "}
        <a href="/dons/">page de dons</a>.
        <Spacer size="0.5rem" />
        Vous pouvez déjà créer une demande, mais vous ne pourrez la faire
        valider que lorsque votre allocation sera suffisante.
      </div>

      <Spacer size="1rem" />
      <Buttons>
        <Button as="a" href={group?.routes?.donations}>
          Allouer un don
        </Button>
        {group?.routes?.createSpendingRequest && (
          <Button as="a" href={group.routes.createSpendingRequest} $wrap>
            Je crée une demande de dépense
          </Button>
        )}
      </Buttons>

      <Spacer size="1rem" />

      <StyledTitle>
        {withGroupWord`Solliciter des dons pour mon groupe`}
      </StyledTitle>

      <span style={{ color: style.black700 }}>
        {withGroupWord`Partagez ce lien pour solliciter des dons pour votre groupe :`}
      </span>

      <ShareLink
        color="primary"
        label="Copier le lien"
        url={group?.routes?.donations}
      />
    </>
  );
};
GroupFinancePage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupFinancePage;
