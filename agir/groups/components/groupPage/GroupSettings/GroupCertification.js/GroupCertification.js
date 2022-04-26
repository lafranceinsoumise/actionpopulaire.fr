import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { CERTIFICATION_CRITERIA } from "@agir/groups/utils/group";

const StyledWarning = styled.div`
  font-size: 0.875rem;
  color: ${(props) => props.theme.black700};
  background-color: ${(props) => props.theme.secondary100};
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;

  strong {
    font-weight: 600;
  }
`;

const StyledContent = styled.article`
  color: ${(props) => props.theme.black700};

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
    gap: 1.25rem;

    li {
      display: flex;
      flex-flow: row nowrap;
      align-items: flex-start;
      gap: 1rem;
      font-size: 1rem;

      ${RawFeatherIcon} {
        flex: 0 0 2rem;
        color: white;
        border-radius: 100%;
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      strong {
        font-weight: 600;
        color: ${(props) => props.theme.black1000};
      }
    }
  }

  footer {
    width: 100%;
    text-align: center;
    font-size: 0.875rem;

    ${Button} {
      &[disabled] {
        opacity: 0.3;
      }
    }
  }
`;

const MissingCriteriaWarning = () => (
  <StyledWarning>
    <strong>
      Action requise&nbsp;: votre groupe ne respecte plus la charte des groupes
      d'action.
    </strong>{" "}
    Certains des critères requis pour la certification de votre groupe ne sont
    plus respectés.
  </StyledWarning>
);

const GroupCertification = (props) => {
  const { certificationRequestURL, isCertified, criteria } = props;

  const certificationCriteria = useMemo(
    () =>
      Object.keys(criteria)
        .sort(
          (a, b) =>
            Object.keys(CERTIFICATION_CRITERIA).indexOf(b) -
            Object.keys(CERTIFICATION_CRITERIA).indexOf(a)
        )
        .map((key) => ({
          ...(CERTIFICATION_CRITERIA[key] || {}),
          key,
          checked: criteria[key],
        })),
    [criteria]
  );

  const checkedCriteria = certificationCriteria.filter(
    (criterion) => criterion.checked
  );
  const isCertifiable = checkedCriteria.length === certificationCriteria.length;

  return (
    <>
      <StyledTitle>Certification du groupe</StyledTitle>
      <Spacer size="0.5rem" />
      <StyledContent>
        <p>
          La certification du groupe permet de recevoir un code mensuel de 30
          euros afin de <Link route="materiel">commander du matériel</Link>.
        </p>
        <p>
          Par ailleurs, la certification permet de témoigner du respect de la{" "}
          <Link route="charteEquipes">charte des groupes d’action</Link>.
        </p>
        {isCertified && !isCertifiable && <MissingCriteriaWarning />}
        <Spacer size="1rem" />
        <ul>
          {certificationCriteria.map(({ key, checked, label, description }) => (
            <li key={key}>
              <RawFeatherIcon
                name={checked ? "check" : "chevron-right"}
                css={`
                  background-color: ${({ name, theme }) =>
                    name === "check" ? theme.green500 : theme.black500};
                `}
              />
              <span>
                <strong>{label || key}</strong>
                <br />
                {description}
              </span>
            </li>
          ))}
        </ul>
        <Spacer size="2rem" />
        {!isCertified && certificationRequestURL && (
          <footer>
            <Button
              link
              color="primary"
              href={certificationRequestURL}
              disabled={!isCertifiable}
            >
              Demander la certification
            </Button>
            <Spacer size="1rem" />
            <span>
              {checkedCriteria.length === 0
                ? "Aucune"
                : `${checkedCriteria.length}/${certificationCriteria.length}`}{" "}
              {checkedCriteria.length <= 1
                ? "condition remplie"
                : "conditions remplies"}{" "}
              pour demander la certification
            </span>
          </footer>
        )}
      </StyledContent>
    </>
  );
};
GroupCertification.propTypes = {
  isCertified: PropTypes.bool,
  certificationRequestURL: PropTypes.string,
  criteria: PropTypes.shape({
    genderBalance: PropTypes.bool,
    activity: PropTypes.bool,
    members: PropTypes.bool,
    seasoned: PropTypes.bool,
  }),
};
export default GroupCertification;
