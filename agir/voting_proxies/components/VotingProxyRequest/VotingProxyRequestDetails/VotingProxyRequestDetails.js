import PropTypes from "prop-types";
import React from "react";
import { useLocation } from "react-router-dom";
import useSWR from "swr";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import StyledPageContainer from "@agir/voting_proxies/Common/StyledPageContainer";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage";
import VotingProxyWidget from "./VotingProxyWidget";

import { getVotingProxyEndpoint } from "@agir/voting_proxies/Common/api";

const groupRequestByProxy = (requests) => {
  const byProxy = {};

  requests.forEach((request) => {
    byProxy[request.votingProxy.id] = byProxy[request.votingProxy.id] || {
      ...request.votingProxy,
      status: request.status,
      votingProxyRequests: [],
      votingDates: [],
    };
    byProxy[request.votingProxy.id].votingProxyRequests.push(request);
    byProxy[request.votingProxy.id].votingDates.push(request.votingDate);
  });

  return Object.values(byProxy);
};

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
      votingProxyRequestsIds && { vpr: votingProxyRequestsIds }
    ),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  if (error?.response?.status === 404) {
    // The voting proxy does not exist or is no longer available
    return <NotFoundPage isTopBar={false} reloadOnReconnection={false} />;
  }

  return (
    <StyledPageContainer>
      <div
        css={`
          padding: 1rem;
        `}
      >
        <PageFadeIn ready={typeof data !== "undefined"} wait={<Skeleton />}>
          {data && (
            <>
              <h2
                css={`
                  color: ${({ theme }) => theme.primary500};
                `}
              >
                Établissez votre procuration
              </h2>
              <Spacer size="1.5rem" />
              <p>Vos demandes de procuration de vote ont été acceptées.</p>
              <h5>Maintenant&nbsp;:</h5>
              <ol>
                <li>
                  Recevez les informations personnelles de la personne qui
                  accepté de voter pour vous par SMS
                </li>
                <li>Remplissez votre procuration en ligne</li>
                <li>
                  Déplacez-vous en commissariat ou gendarmerie pour vérifier
                  votre identité et valider la procuration
                </li>
                <li>
                  Une fois la procuration validée, prévenez le ou la volontaire.
                </li>
              </ol>
              <Spacer size="3rem" />
              <div
                css={`
                  text-align: center;
                `}
              >
                <Button
                  link
                  wrap
                  href="https://www.maprocuration.gouv.fr/"
                  target="_blank"
                  rel="noopener noreferrer"
                  color="success"
                  css={`
                    font-size: 1.25rem;
                    height: 4.25rem;
                    padding: 0 2.5rem;
                    line-height: 1.2;
                  `}
                >
                  Établir la procuration&ensp;
                  <RawFeatherIcon name="external-link" />
                </Button>
                <p
                  css={`
                    padding: 0.5rem 0;
                    font-size: 0.875rem;
                    color: ${({ theme }) => theme.black500};
                  `}
                >
                  en 2mn sur le site du service public
                </p>
              </div>
              <Spacer size="1.5rem" />
              <div
                css={`
                  display: flex;
                  flex-flow: column nowrap;
                  gap: 1rem;
                `}
              >
                {groupRequestByProxy(data).map((proxy) => (
                  <VotingProxyWidget key={proxy.id} {...proxy} />
                ))}
              </div>
              <Spacer size="1.5rem" />
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
                  </a>
                </p>
              </footer>
            </>
          )}
        </PageFadeIn>
      </div>
    </StyledPageContainer>
  );
};
VotingProxyRequestDetails.propTypes = {};
export default VotingProxyRequestDetails;
