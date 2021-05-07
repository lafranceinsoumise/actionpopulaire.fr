import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";
import DiscountCode from "./DiscountCode";

import { StyledTitle } from "./styledComponents.js";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";
import { useGroupWord } from "@agir/groups/utils/group";

const StyledDiscountCodeList = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 1rem;
`;

const GroupMaterielPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const group = useGroup(groupPk);
  const withGroupWord = useGroupWord(group);

  const ordersURL = useMemo(() => group?.routes?.orders || "", [group]);
  const discountCodes = useMemo(
    () =>
      Array.isArray(group?.discountCodes)
        ? _sortBy(group.discountCodes, "expirationDate")
        : [],
    [group]
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Matériel</StyledTitle>
      <span style={{ color: style.black700 }}>
        {withGroupWord`Accédez à du matériel (affiche, tracts, autocollants...) gratuit en
          utilisant les codes promos mis à disposition de votre groupe.`}
      </span>
      {ordersURL && (
        <>
          <Spacer size=".5rem" />
          <span style={{ color: style.black700 }}>
            Pour utiliser vos codes, accédez au site matériel&nbsp;:
          </span>
          <Spacer size="1.5rem" />
          <p style={{ textAlign: "center" }}>
            <Button
              icon="external-link"
              color="primary"
              as="a"
              href={ordersURL}
            >
              Site d’achat de matériel
            </Button>
          </p>
        </>
      )}
      <Spacer size="2.5rem" />
      <StyledDiscountCodeList>
        {discountCodes.map((discountCode) => (
          <DiscountCode key={discountCode.code} {...discountCode} />
        ))}
      </StyledDiscountCodeList>
    </>
  );
};
GroupMaterielPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupMaterielPage;
