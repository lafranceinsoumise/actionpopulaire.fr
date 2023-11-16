import React, { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import _debug from "debug";

import Button from "@agir/front/genericComponents/Button";
import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";

import {
  DECISIONS,
  REVERSE_DECISIONS,
  ELU_STATUTS,
  InfosElu,
  ISSUE,
  RequestStatus,
} from "../types";
import { modifierParrainage } from "../queries";
import { CadreAvertissement, Error } from "../utils";

const debug = _debug("elus:parrainages:FicheElu:Formulaire");

const BoutonAnnuler = ({ elu, onStatusChange }) => {
  const [state, setState] = useState(RequestStatus.IDLE());
  const annuler = useCallback(async () => {
    try {
      setState(RequestStatus.LOADING());
      await modifierParrainage(elu.idRechercheParrainage, {
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
          if (!state.loading) {
            annuler();
          }
        }}
      >
        Annuler le contact
      </a>
      {state.loading && <AnimatedMoreHorizontal />}
      {state.hasError && <Error>{state.message}</Error>}
    </>
  );
};

BoutonAnnuler.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

const Formulaire = ({ elu, onStatusChange }) => {
  // indique si une requête est en cours ou a échoué.
  const [requestState, setRequestState] = useState(RequestStatus.IDLE());

  // la valeur actuelle du champ décision
  const [decision, setDecision] = useState();

  // retient si la saisie actuelle a été enregistrée
  const [sauvegarde, setSauvegarde] = useState(false);

  // les références aux deux champs non contrôlés
  const formulaireInput = useRef();
  const commentairesInput = useRef();

  // il faut réinitialiser le formulaire quand l'élu change
  useEffect(() => {
    const initialDecision =
      elu.rechercheParrainage &&
      (elu.rechercheParrainage.statut !== ISSUE.ENGAGEMENT
        ? REVERSE_DECISIONS[elu.rechercheParrainage.statut]
        : elu.rechercheParrainage.lienFormulaire
          ? DECISIONS[0]
          : DECISIONS[1]);

    setDecision(initialDecision);
    setSauvegarde(false);
    commentairesInput.current.value =
      elu.rechercheParrainage?.commentaires || "";
  }, [elu]);

  const soumettreFormulaire = useCallback(
    async (e) => {
      e.preventDefault();
      setRequestState(RequestStatus.LOADING());

      const formulaire =
        decision &&
        decision.formulaire &&
        formulaireInput.current.files.length > 0
          ? formulaireInput.current.files[0]
          : null;

      const commentaires = commentairesInput.current.value;

      try {
        const res = await modifierParrainage(elu.idRechercheParrainage, {
          statut: decision.value,
          commentaires,
          formulaire,
        });
        setRequestState(RequestStatus.IDLE());
        setSauvegarde(true);
        onStatusChange({
          ...elu,
          statut: ELU_STATUTS.PERSONNELLEMENT_VU,
          rechercheParrainage: res,
        });
      } catch (e) {
        setRequestState(RequestStatus.ERROR(e.message));
      }
    },
    [elu, decision, onStatusChange],
  );

  return (
    <div>
      {elu.statut === ELU_STATUTS.A_CONTACTER && (
        <>
          <BoutonAnnuler elu={elu} onStatusChange={onStatusChange} />
          <CadreAvertissement>
            <p>
              <strong>Contactez {elu.nomComplet}</strong> à propos de la
              signature de parrainage des élu⋅es pour la candidature de Jean-Luc
              Mélenchon.
            </p>
            <p>
              <strong>Conseil</strong> : Utilisez{" "}
              <a href="https://melenchon2022.fr/le-guide-de-la-recherche-des-parrainages/">
                la documentation
              </a>{" "}
              pour vous aider dans votre discours. Il faut{" "}
              <strong>rencontrer physiquement le maire</strong> pour une
              entrevue républicaine. Vous devrez souvent aller à sa rencontre
              quand il est en mairie ou dans son village.
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
        </>
      )}
      <form onSubmit={soumettreFormulaire}>
        <h4>Conclusion de l'échange</h4>
        {DECISIONS.map((d) => (
          <label htmlFor={d.id} key={d.id}>
            <input
              type="radio"
              name="statut"
              id={d.id}
              checked={d.id === decision?.id}
              onChange={() => {
                setDecision(d);
                setSauvegarde(false);
              }}
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
          onChange={() => sauvegarde && setSauvegarde(false)}
        />

        {decision && decision.formulaire && (
          <>
            <label className="title" htmlFor="formulaire">
              Formulaire signé
            </label>
            {elu.rechercheParrainage?.lienFormulaire && (
              <a href={elu.rechercheParrainage.lienFormulaire} target="_blank">
                Formulaire actuel
              </a>
            )}

            <input
              id="formulaire"
              type="file"
              name="formulaire"
              ref={formulaireInput}
              required={true}
              onChange={() => sauvegarde && setSauvegarde(false)}
            />
          </>
        )}
        <Button
          color="primary"
          disabled={sauvegarde || requestState.loading || decision === null}
          block
        >
          {sauvegarde
            ? "Enregistré !"
            : elu.statut === ELU_STATUTS.A_CONTACTER
              ? "Envoyer les informations"
              : "Mettre à jour les informations"}
        </Button>
        {requestState.loading && <AnimatedMoreHorizontal />}
        {requestState.hasError && <Error>{requestState.message}</Error>}
      </form>
    </div>
  );
};

Formulaire.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};

export default Formulaire;
