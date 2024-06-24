import React from "react";

import Button from "@agir/front/genericComponents/Button";
import FormSuccess from "@agir/elections/Common/FormSuccess";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewPollingStationOfficerSuccess = () => (
  <FormSuccess>
    <h2>Votre demande a été envoyée​</h2>
    <Spacer size="0.875rem" />
    <p>
      Les équipes militantes locales recevront bientôt votre demande et pourront
      vous recontacter.
    </p>
    <Spacer size="0.875rem" />
    <p>
      Merci beaucoup, c'est grâce à votre implication que nous pouvons
      participer à assurer la sincérité du scrutin. C'est une tâche politique
      importante&nbsp;!​
    </p>
    <Spacer size="1rem" />
    <p>
      <strong>
        Soyons dans tous les bureaux de vote&nbsp;:
        <br />
        n'hésitez pas à partager ce formulaire​&nbsp;!
      </strong>
    </p>
    <Spacer size="1.5rem" />
    <ShareCard
      style={{ margin: "0 auto", maxWidth: "600px", textAlign: "left" }}
      title="Partager ce formulaire :"
    />
    <Spacer size="1rem" />
    <p
      css={`
        max-width: 600px;
        margin: 0 auto;
        font-size: 0.875rem;
        background-color: ${({ theme }) => theme.primary50};
        padding: 1rem;
        border-radius: ${({ theme }) => theme.borderRadius};
        text-align: center;
      `}
    >
      <strong
        css={`
          color: ${({ theme }) => theme.primary500};
        `}
      >
        Explorez les ressources pour les délégué·es et assesseur·es​
      </strong>
      <Spacer size=".75rem" />
      <span
        css={`
          display: inline-flex;
          gap: 0.5rem;

          @media (max-width: ${({ theme }) => theme.collapse}px) {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          }
        `}
      >
        <Button
          link
          small
          color="primary"
          icon="youtube"
          href="https://www.youtube.com/watch?v=eU6tYjFOrEQ"
          target="_blank"
          rel="noopener noreferrer"
        >
          La vidéo de formation
        </Button>
        <Button
          link
          small
          color="primary"
          icon="file-text"
          route="pollingStationOfficerGuide"
          target="_blank"
          rel="noopener noreferrer"
        >
          Le guide PDF
        </Button>
      </span>
    </p>
  </FormSuccess>
);

export default NewPollingStationOfficerSuccess;
