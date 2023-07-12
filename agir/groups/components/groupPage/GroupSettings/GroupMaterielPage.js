import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";

import DiscountCode from "./DiscountCode";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";
import { parseDiscountCodes } from "../utils";

const StyledDiscountCodeList = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 1rem;
`;

const GroupMaterielPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const group = useGroup(groupPk);

  const ordersURL = useMemo(() => group?.routes?.orders || "", [group]);
  const [discountCodes, specialDiscountCodes] = useMemo(
    () => parseDiscountCodes(group?.discountCodes),
    [group],
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Matériel</StyledTitle>
      <span style={{ color: style.black700 }}>
        Accédez à du matériel (affiches, tracts, autocollants...) gratuit en
        utilisant les codes promos mis à disposition de votre groupe.
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
              link
              href={ordersURL}
              target="_blank"
              rel="noopener noreferrer"
              wrap
            >
              Site d’achat de matériel
            </Button>
          </p>
        </>
      )}
      <Spacer size="2rem" />
      <StyledDiscountCodeList>
        {specialDiscountCodes.map((discountCode) => (
          <DiscountCode key={discountCode.code} {...discountCode} />
        ))}
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
