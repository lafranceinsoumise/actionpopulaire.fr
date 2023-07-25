import PropTypes from "prop-types";
import React from "react";
import useSWRImmutable from "swr/immutable";
import styled from "styled-components";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { getGroupEndpoint } from "@agir/groups/utils/api";
import BackLink from "@agir/front/app/Navigation/BackLink";
import { Button } from "@agir/donations/common/StyledComponents";

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;

  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;

    & > * {
      margin: 0;
    }

    strong {
      font-weight: inherit;
      text-decoration: underline;
    }

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.375rem;
      margin: 0 0 1.25rem;
    }
  }
`;

const CreateSpendingRequestPage = ({ groupPk }) => {
  const { data: group, isLoading } = useSWRImmutable([
    getGroupEndpoint("getGroup", { groupPk }),
  ]);

  console.log(group);

  return (
    <PageFadeIn ready={!isLoading} wait={<Skeleton />}>
      <StyledPage>
        <nav>
          <BackLink />
          <Button
            link
            color="link"
            icon="arrow-right"
            route="spendingRequestHelp"
          >
            Un doute ? Consultez le <strong>centre d'aide</strong>
          </Button>
        </nav>
        <h2>Nouvelle dépense</h2>
      </StyledPage>
    </PageFadeIn>
  );
};

CreateSpendingRequestPage.propTypes = {
  groupPk: PropTypes.string,
};

export default CreateSpendingRequestPage;
