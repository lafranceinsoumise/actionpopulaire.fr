import React, { useCallback, useState } from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

import Button from "@agir/front/genericComponents/Button";
import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";

import { ELU_STATUTS, InfosElu, RequestStatus, StatutPill } from "../types";
import { creerRechercheParrainage } from "../queries";
import Formulaire from "./Formulaire";
import { MarginBlock, Error } from "../utils";

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

const InteractionBoxLayout = styled(MarginBlock)`
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
          <Formulaire elu={elu} onStatusChange={onStatusChange} />
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

  ${MarginBlock} {
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

const ColonneCentree = styled.div`
  margin: 0 auto;
  max-width: 600px;
`;

const FicheElu = ({ elu, onStatusChange }) => {
  const mairie = elu.mairie;
  const distance = elu.distance?.toLocaleString?.("fr-FR", {
    maximumFractionDigits: 1,
  });

  return (
    <Layout>
      <ColonneCentree>
        <h2>{elu.nomComplet}</h2>
        <div className="subtitle">
          {elu.titre} — {elu.commune}{" "}
          {distance ? (
            elu.distance > 0.1 ? (
              `(à ${distance} km)`
            ) : (
              "(à moins de 100m)"
            )
          ) : (
            <em>
              (<a href="/profil/identite/">indiquez où vous êtes</a> pour voir
              la distance)
            </em>
          )}
        </div>
        <MarginBlock>
          <StatutPill statut={elu.statut} />
        </MarginBlock>
        <InteractionBox elu={elu} onStatusChange={onStatusChange} />
        {mairie.adresse && (
          <MarginBlock>
            <h3>Adresse de la mairie</h3>
            <div style={{ lineSpace: "pre-wrap" }}>{mairie.adresse}</div>
          </MarginBlock>
        )}
        {mairie.telephone && (
          <MarginBlock>
            <h3>Numéro de téléphone de la mairie</h3>
            <div>{mairie.telephone}</div>
          </MarginBlock>
        )}
        {mairie.email && (
          <MarginBlock>
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
          </MarginBlock>
        )}
        {mairie.horaires && mairie.horaires.length !== 0 && (
          <MarginBlock>
            <h3>Horaires d'ouverture de la mairie</h3>
            <Horaires horaires={mairie.horaires} />
          </MarginBlock>
        )}
      </ColonneCentree>
    </Layout>
  );
};

FicheElu.propTypes = {
  elu: InfosElu,
  onStatusChange: PropTypes.func,
};
FicheElu.Layout = Layout;

export default FicheElu;
