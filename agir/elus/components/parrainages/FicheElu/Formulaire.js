import React, { useCallback, useRef, useState } from "react";
import PropTypes from "prop-types";

import Button from "@agir/front/genericComponents/Button";
import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";

import {
  DECISIONS,
  ELU_STATUTS,
  InfosElu,
  ISSUE,
  RequestStatus,
} from "../types";
import { terminerParrainage } from "../queries";
import { CadreAvertissement, Error } from "../utils";

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

const Formulaire = ({ elu, onStatusChange }) => {
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
          pour vous aider dans votre discours. Il faut{" "}
          <strong>rencontrer physiquement le maire</strong> pour une entrevue
          républicaine. Vous devrez souvent aller à sa rencontre quand il est en
          mairie ou dans son village.
        </p>
        <p>
          <em>
            Il est souvent inutile de chercher à prendre rendez-vous par
            téléphone
          </em>{" "}
          car c'est souvent utilisé par les mairies pour décliner la
          proposition. Déplacez-vous en mairie pour de meilleurs résultats !
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

Formulaire.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

export default Formulaire;
