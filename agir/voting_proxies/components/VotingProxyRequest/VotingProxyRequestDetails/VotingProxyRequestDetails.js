import React from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";
import useSWR from "swr";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import StyledPageContainer from "@agir/elections/Common/StyledPageContainer";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";
import VotingProxyWidget from "./VotingProxyWidget";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";
import SecurityWarning from "@agir/voting_proxies/Common/SecurityWarning";

import { getVotingProxyEndpoint } from "@agir/voting_proxies/Common/api";

import { votingProxyRequestTheme } from "@agir/voting_proxies/Common/themes";

const StyledList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: start;
    gap: 1rem;

    & > :first-child {
      flex: 0 0 auto;
      color: ${(props) => props.theme.primary500};
    }
  }
`;

const getVotingProxyRequestsIdsFromURLSearchParams = (search) => {
  if (!search) {
    return null;
  }
  const searchParams = new URLSearchParams(search);
  const ids = searchParams.get("vpr");
  if (!ids) {
    return null;
  }
  return ids;
};

const VotingProxyRequestDetails = () => {
  const { search } = useLocation();
  const votingProxyRequestsIds =
    getVotingProxyRequestsIdsFromURLSearchParams(search);

  const { data, error } = useSWR(
    getVotingProxyEndpoint(
      "acceptedVotingProxyRequests",
      null,
      votingProxyRequestsIds && { vpr: votingProxyRequestsIds },
    ),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  if (error?.response?.status === 404) {
    // The voting proxy does not exist or is no longer available
    return <NotFoundPage hasTopBar={false} reloadOnReconnection={false} />;
  }

  return (
    <StyledPageContainer theme={votingProxyRequestTheme}>
      <PageFadeIn ready={typeof data !== "undefined"} wait={<Skeleton />}>
        {data && (
          <>
            <h2>
              {data.length === 1
                ? "Votre demande de procuration"
                : "Vos demandes de procuration"}
            </h2>
            <Spacer size="1rem" />
            <WarningBlock background="#ffe8d7" iconColor="#ff8c37">
              Une fois qu'une personne a accepté de voter à votre place,{" "}
              <strong
                style={{
                  fontWeight: 600,
                  boxShadow: "inset 0 -3px 0 0 currentcolor",
                }}
              >
                vous devez faire une demande de procuration et la faire valider
                auprès des autorités
              </strong>{" "}
              (dans commissariat de police, une gendarmerie ou un consulat
              français) . Retrouvez tous les détails sur la procédure officielle
              sur{" "}
              <Link
                href="https://maprocuration.gouv.fr"
                target="_blank"
                rel="noopener noreferrer"
              >
                le site du service public
              </Link>
            </WarningBlock>
            <Spacer size="1rem" />
            <p>
              {data.length === 1
                ? "Votre demande de procuration de vote a été acceptée."
                : "Vos demandes de procuration de vote ont été acceptées."}{" "}
              Maintenant&nbsp;:
            </p>
            <Spacer size="1rem" />
            <StyledList>
              <li>
                <FeatherIcon name="arrow-right" />
                <span>
                  Recevez les informations personnelles de la personne qui a
                  accepté de voter pour vous par SMS et par e-mail en cliquant
                  sur le bouton ci-dessous
                </span>
              </li>
              <li>
                <FeatherIcon name="arrow-right" />
                <span>
                  Remplissez votre procuration sur{" "}
                  <Link
                    href="https://www.maprocuration.gouv.fr/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontWeight: 600 }}
                  >
                    le site du service public
                  </Link>{" "}
                  (environ 3 min.)
                </span>
              </li>
              <li>
                <FeatherIcon name="arrow-right" />
                <span>
                  Déplacez-vous au commissariat, à la gendarmerie ou au consulat
                  pour vérifier votre identité et valider la procuration{" "}
                  <strong
                    style={{
                      fontWeight: 600,
                      boxShadow: "inset 0 -3px 0 0 currentcolor",
                    }}
                  >
                    avant le 27 juin pour le premier tour et le 4 juillet pour
                    le second
                  </strong>
                </span>
              </li>
              <li>
                <FeatherIcon name="arrow-right" />
                <span>
                  Une fois la procuration validée, prévenez le ou la volontaire
                  à l'aide du bouton ci-dessous
                </span>
              </li>
            </StyledList>
            <Spacer size="1rem" />
            <SecurityWarning />
            <Spacer size="1rem" />
            <div
              css={`
                display: flex;
                flex-flow: column nowrap;
                gap: 1rem;
              `}
            >
              {data.map((request) => (
                <VotingProxyWidget key={request.id} request={request} />
              ))}
            </div>
            <Spacer size="2rem" />
            <footer
              css={`
                font-size: 0.875rem;
                color: ${({ theme }) => theme.black500};
              `}
            >
              <p>
                Si vous n’avez pas de compte France Connect, vous pouvez aussi
                imprimer et compléter{" "}
                <a
                  href="https://www.formulaires.service-public.fr/gf/cerfa_14952.do"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  le formulaire papier
                </a>{" "}
                avant de vous déplacer en commissariat ou gendarmerie.
              </p>
              <Spacer size="1rem" />
              <p>
                Une question ? Accédez à la{" "}
                <a
                  href="https://www.maprocuration.gouv.fr/#FAQ"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  FAQ de MaProcuration.gouv.fr
                </a>{" "}
                ou écrivez-nous à l'adresse{" "}
                <a href="mailto:procurations@actionpopulaire.fr">
                  procurations@actionpopulaire.fr
                </a>
                .
              </p>
            </footer>
          </>
        )}
      </PageFadeIn>
    </StyledPageContainer>
  );
};
VotingProxyRequestDetails.propTypes = {};
export default VotingProxyRequestDetails;
