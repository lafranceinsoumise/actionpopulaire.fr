import React, { useCallback, useRef, useState } from "react";
import styled from "styled-components";
import PropTypes from "prop-types";
import { InfosElu } from "@agir/elus/parrainages/types";
import {
  DECISIONS,
  ELU_STATUTS,
  ISSUE,
  RequestStatus,
  StatutPill,
} from "./types";
import Button from "@agir/front/genericComponents/Button";
import { creerRechercheParrainage, terminerParrainage } from "./queries";
import AnimatedMoreHorizontal from "../../../front/components/genericComponents/AnimatedMoreHorizontal";

const Presentation = () => (
  <div>
    <img
      src="/static/parrainages/recherche_parrainages.png"
      alt="Une femme qui tient trois formulaires de promesse de parrainage."
    />
    <h2>Collecte des parrainages</h2>
    <p>
      Interface d’organisation pour l’obtention des 500 signatures pour la
      candidature de Jean-Luc Mélenchon aux présidentielles de 2022.
    </p>
    <ol>
      <li>
        Choisissez un⋅e élu⋅e disponible, c'est-à-dire que personne d'autre n'a
        encore prévu de contacter
      </li>
      <li>
        Confirmez que vous comptez le ou la contacter. Ce sera votre
        responsabilité !
      </li>
      <li>
        Une fois que vous aurez rencontré l'élu, n'oubliez pas de nous indiquer
        la conclusion de l'échange dans cette même interface
      </li>
    </ol>
  </div>
);

const HorairesList = styled.ul`
  list-style-type: none;
  margin: 0;
  padding: 0;
`;

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const Horaires = ({ horaires }) => {
  return (
    <HorairesList>
      {horaires.map(([j1, j2, hs]) => {
        const jours = j1 === j2 ? capitalize(j1) : `${capitalize(j1)} au ${j2}`;
        const heures = hs
          .map(([h1, h2]) => `${h1.slice(0, 5)} — ${h2.slice(0, 5)}`)
          .join(" et ");
        return (
          <li key={jours}>
            {jours} : {heures}
          </li>
        );
      })}
    </HorairesList>
  );
};
Horaires.propTypes = {
  horaires: PropTypes.array,
};

const Block = styled.div`
  margin: 24px 0;
`;

const Error = styled.div`
  color: ${(props) => props.theme.redNSP};
  font-weight: 500;
`;

const CadreAvertissement = styled.div`
  background-color: ${(props) => props.theme.black50};
  margin: 20px 0;
  padding: 1rem;
`;

const BoutonCreerParrainage = ({ elu, onStatusChange }) => {
  const [state, setState] = useState(RequestStatus.IDLE());
  const callback = useCallback(async () => {
    setState(RequestStatus.LOADING());
    try {
      const res = await creerRechercheParrainage(elu.id);
      setState(RequestStatus.IDLE());
      onStatusChange({
        ...elu,
        statut: ELU_STATUTS.A_CONTACTER,
        idRechercheParrainage: res.id,
      });
    } catch (e) {
      setState(RequestStatus.ERROR(e.message));
    }
  }, [elu, onStatusChange]);

  return (
    <div>
      <Button color="primary" onClick={callback} disabled={state.isLoading}>
        Je m'en occupe !
      </Button>
      {state.isLoading && <AnimatedMoreHorizontal />}
      {state.isError && <Error>{state.message}</Error>}
    </div>
  );
};
BoutonCreerParrainage.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

const BoutonAnnuler = ({ elu, onStatusChange }) => {
  const [state, setState] = useState(RequestStatus.IDLE());
  const annuler = useCallback(async () => {
    try {
      setState(RequestStatus.LOADING());
      await terminerParrainage(elu.idRechercheParrainage, {
        statut: ISSUE.ANNULE,
      });
      onStatusChange({
        ...elu,
        idRechercheParrainage: null,
        statut: ELU_STATUTS.DISPONIBLE,
      });
      setState(RequestStatus.IDLE());
    } catch (e) {
      setState(RequestStatus.ERROR(e.message));
    }
  }, [elu, onStatusChange]);

  return (
    <>
      <a
        href="#"
        onClick={(e) => {
          e.preventDefault();
          if (!state.isLoading) {
            annuler();
          }
        }}
      >
        Annuler le contact
      </a>
      {state.isLoading && <AnimatedMoreHorizontal />}
      {state.isError && <Error>{state.message}</Error>}
    </>
  );
};

BoutonAnnuler.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

const FormulaireTerminerParrainage = ({ elu, onStatusChange }) => {
  const [state, setState] = useState(RequestStatus.IDLE());
  const [decision, setDecision] = useState(null);
  const formulaireInput = useRef();
  const commentairesInput = useRef();

  const soumettreFormulaire = useCallback(
    async (e) => {
      e.preventDefault();
      setState(RequestStatus.LOADING());

      const formulaire =
        decision &&
        decision.formulaire &&
        formulaireInput.current.files.length > 0
          ? formulaireInput.current.files[0]
          : null;

      const commentaires = commentairesInput.current.value;

      try {
        await terminerParrainage(elu.idRechercheParrainage, {
          statut: decision.value,
          commentaires,
          formulaire,
        });
        setState(RequestStatus.IDLE());
        onStatusChange({
          ...elu,
          statut: ELU_STATUTS.PERSONNELLEMENT_VU,
        });
      } catch (e) {
        setState(RequestStatus.ERROR(e.message));
      }
    },
    [elu, decision, onStatusChange]
  );

  return (
    <div>
      <BoutonAnnuler elu={elu} onStatusChange={onStatusChange} />
      <CadreAvertissement>
        <p>
          <strong>Contactez {elu.nomComplet}</strong> à propos de la signature
          de parrainage des élu⋅es pour la candidature de Jean-Luc Mélenchon.
        </p>
        <p>
          <strong>Conseil</strong> : Utilisez{" "}
          <a href="https://melenchon2022.fr/le-guide-de-la-recherche-des-parrainages/">
            la documentation
          </a>{" "}
          pour vous aider dans votre discours . Prenez rendez-vous par
          téléphone, et <strong>déplacez-vous en mairie</strong> pour de
          meilleurs résultats !
        </p>
      </CadreAvertissement>
      <form onSubmit={soumettreFormulaire}>
        <h4>Conclusion de l'échange</h4>
        {DECISIONS.map((d) => (
          <label htmlFor={d.id} key={d.id}>
            <input
              type="radio"
              name="statut"
              id={d.id}
              checked={decision && d.id === decision.id}
              onChange={() => setDecision(d)}
            />{" "}
            {d.label}
          </label>
        ))}

        <label className="title" htmlFor="commentaires">
          {(decision && decision.commentairesTitre) || "Commentaires"}
        </label>
        <textarea
          id="commentaires"
          name="commentaires"
          ref={commentairesInput}
          required={decision && decision.commentairesRequis}
        />

        {decision && decision.formulaire && (
          <>
            <label className="title" htmlFor="formulaire">
              Formulaire signé
            </label>
            <input
              id="formulaire"
              type="file"
              name="formulaire"
              ref={formulaireInput}
              required={true}
            />
          </>
        )}
        <Button
          color="primary"
          disabled={state.isLoading || decision === null}
          block
        >
          Envoyer les informations
        </Button>
        {state.isLoading && <AnimatedMoreHorizontal />}
        {state.isError && <Error>{state.message}</Error>}
      </form>
    </div>
  );
};

FormulaireTerminerParrainage.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

const InteractionBoxLayout = styled(Block)`
  border: 1px solid ${(props) => props.theme.black200};
  padding: 20px;
`;

const InteractionBox = ({ elu, onStatusChange }) => {
  const demonstratif = elu.sexe === "F" ? "cette élue" : "cet élu";

  switch (elu.statut) {
    case "D":
      return (
        <InteractionBoxLayout>
          <p>Personne n'a indiqué s'occuper de {demonstratif}.</p>
          <BoutonCreerParrainage elu={elu} onStatusChange={onStatusChange} />
        </InteractionBoxLayout>
      );
    case "E":
      return (
        <InteractionBoxLayout>
          Quelqu'un d'autre a indiqué s'occuper de contacter {demonstratif}
          👍
        </InteractionBoxLayout>
      );
    case "A":
      return (
        <InteractionBoxLayout>
          <FormulaireTerminerParrainage
            elu={elu}
            onStatusChange={onStatusChange}
          />
        </InteractionBoxLayout>
      );
    case "T":
      return (
        <InteractionBoxLayout>
          Quelqu'un d'autre s'est déjà chargé de contacter {demonstratif}
        </InteractionBoxLayout>
      );
    case "P":
      return (
        <InteractionBoxLayout>
          Merci de vous être occupé⋅e de contacter cette personne &#x1F680;
        </InteractionBoxLayout>
      );
  }
};
InteractionBox.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

const Layout = styled.div`
  padding: 60px;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 0 35px;
  }

  ${Block} {
    font-size: 16px;
  }

  h2 {
    margin-bottom: 0.5rem;
  }
  .subtitle {
    font-size: 16px;
    margin-bottom: 30px;
  }

  h3 {
    margin-bottom: 0;
  }

  label {
    display: block;
    margin: 0;
    font-weight: 400;
  }

  label.title,
  h4 {
    font-weight: 700;
    font-size: 14px;
    margin: 20px 0 8px;
  }

  ${Button} {
    margin: 11px 0;
  }
`;

const Container = styled.div`
  margin: 0 auto;
  max-width: 600px;
`;

const FicheElu = ({ elu, onStatusChange }) => {
  if (elu === null || elu === undefined) {
    return (
      <Layout>
        <Container>
          <Presentation />
        </Container>
      </Layout>
    );
  }

  const mairie = elu.mairie;
  const distance = elu.distance?.toLocaleString?.("fr-FR", {
    maximumFractionDigits: 1,
  });

  return (
    <Layout>
      <Container>
        <h2>{elu.nomComplet}</h2>
        <div className="subtitle">
          {elu.titre} — {elu.commune}{" "}
          {distance ? (
            elu.distance > 0.1 && `(à ${distance} km)`
          ) : (
            <em>
              (<a href="/profil/identite/">indiquez où vous êtes</a> pour voir
              la distance)
            </em>
          )}
        </div>
        <Block>
          <StatutPill statut={elu.statut} />
        </Block>
        <InteractionBox elu={elu} onStatusChange={onStatusChange} />
        {mairie.adresse && (
          <Block>
            <h3>Adresse de la mairie</h3>
            <div style={{ lineSpace: "pre-wrap" }}>{mairie.adresse}</div>
          </Block>
        )}
        {mairie.telephone && (
          <Block>
            <h3>Numéro de téléphone de la mairie</h3>
            <div>{mairie.telephone}</div>
          </Block>
        )}
        {mairie.email && (
          <Block>
            <h3>Adresse email de la mairie</h3>
            <div>
              <a
                href={
                  mairie.email.match(/https?:\/\//)
                    ? mairie.email
                    : `mailto:${mairie.email}`
                }
              >
                {mairie.email}
              </a>
            </div>
          </Block>
        )}
        {mairie.horaires && mairie.horaires.length !== 0 && (
          <Block>
            <h3>Horaires d'ouverture de la mairie</h3>
            <Horaires horaires={mairie.horaires} />
          </Block>
        )}
      </Container>
    </Layout>
  );
};

FicheElu.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};
FicheElu.Layout = Layout;

export default FicheElu;
