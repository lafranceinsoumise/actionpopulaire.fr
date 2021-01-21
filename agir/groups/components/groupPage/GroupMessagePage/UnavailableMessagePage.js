import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { routeConfig } from "@agir/front/app/routes.config";
import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import CenteredLayout from "@agir/front/dashboardComponents/CenteredLayout";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getBackLink } from "@agir/front/globalContext/reducers";

const StyledBlock = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  text-align: center;
  max-width: 558px;
  margin: 0 auto;

  @media (max-width: ${style.collapse}px) {
    align-items: stretch;
    padding: 0 1.5rem;
  }

  p {
    margin-bottom: 2rem;
  }

  ${Button} {
    margin-bottom: 1rem;
    text-align: center;
    justify-content: center;
  }
`;

const UnavailableMessagePage = (props) => {
  const { groupPk } = props;

  const backLink = useSelector(getBackLink);

  const groupPageLink = useMemo(
    () =>
      groupPk && routeConfig.groupDetails
        ? routeConfig.groupDetails.getLink({ groupPk })
        : null,
    [groupPk]
  );

  return (
    <CenteredLayout
      backLink={backLink}
      title="Cette discussion n'est pas disponible"
      icon="lock"
    >
      <StyledBlock>
        <p>
          Vous n’avez pas les droits nécessaires pour afficher cette discussion,
          car elle est réservée aux membres du groupe.
        </p>
        {groupPageLink ? (
          <Button color="primary" as="Link" to={groupPageLink}>
            Voir le groupe
          </Button>
        ) : null}
        <Button color="white" as="Link" route="help">
          Voir l'aide en ligne
        </Button>
      </StyledBlock>
    </CenteredLayout>
  );
};

UnavailableMessagePage.propTypes = {
  groupPk: PropTypes.string,
};
export default UnavailableMessagePage;
