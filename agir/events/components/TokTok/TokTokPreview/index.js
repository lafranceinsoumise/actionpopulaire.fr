import React, { useMemo } from "react";
import useSWRImmutable from "swr/immutable";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import {
  Banner,
  BackButton,
  PageContent,
  GroupCreationWarning,
} from "./StyledComponents";
import HowTo from "./HowTo";

const TokTokPreview = () => {
  const { data: session } = useSWRImmutable("/api/session/");

  const isGroupManager = useMemo(
    () =>
      Array.isArray(session?.user?.groups) &&
      session.user.groups.some((group) => group.isManager),
    [session]
  );

  return (
    <div>
      <Banner />
      <PageContent>
        <PageFadeIn
          ready={!!session}
          wait={
            <>
              <Skeleton
                boxes={1}
                style={{ height: 56, marginBottom: "1.5rem" }}
              />
              <Skeleton />
            </>
          }
        >
          <BackButton link route="events">
            Retour à l'accueil
          </BackButton>
          <h2>La carte collaborative du porte-à-porte</h2>
          <HowTo />
          <Spacer size="1.5rem" />
          {!isGroupManager && (
            <>
              <GroupCreationWarning />
              <Spacer size="1.5rem" />
            </>
          )}
          <p
            css={`
              font-size: 0.875rem;
            `}
          >
            Note&nbsp;: TokTok ne remplace pas l’outil d’ajout de contact et le
            formulaire pour indiquer le nombre de soutiens obtenus.
          </p>
          <p
            css={`
              font-size: 0.875rem;
            `}
          >
            TokTok est un outil créé par le{" "}
            <Link
              route="discordInsoumis"
              rel="noopener noreferrer"
              target="_blank"
              css={`
                &,
                &:hover,
                &:focus {
                  color: inherit;
                  text-decoration: underline;
                }
              `}
            >
              Discord Insoumis
            </Link>
          </p>
          <Spacer size="1rem" />
          <p>
            <Button
              link
              block
              route="toktok"
              icon="external-link"
              color="secondary"
            >
              Ouvrir TokTok
            </Button>
            <Spacer size=".5rem" />
            <Button
              link
              block
              route="toktokVideo"
              icon="youtube"
              rel="noopener noreferrer"
              target="_blank"
            >
              Voir la vidéo de présentation
            </Button>
          </p>
        </PageFadeIn>
      </PageContent>
    </div>
  );
};

export default TokTokPreview;
