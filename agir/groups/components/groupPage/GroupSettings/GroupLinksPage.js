import React, { useState, useCallback } from "react";

import Spacer from "@agir/front/genericComponents/Spacer";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import GroupLink from "./GroupLink.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import TextField from "@agir/front/formComponents/TextField";
import Button from "@agir/front/genericComponents/Button";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

const LINKS = [true];
const [NEW_LINK, EDIT_LINK] = [1, 2];

const GroupLinksPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const [config, setConfig] = useState(null);
  const [formData, setFormData] = useState({});

  const group = useGroup(groupPk);

  const handleInputChange = useCallback((e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }, []);

  if ([NEW_LINK, EDIT_LINK].includes(config)) {
    return (
      <>
        <BackButton
          onClick={() => {
            setConfig(null);
          }}
        />
        <StyledTitle>
          {NEW_LINK === config
            ? "Nouveau lien personnalisé"
            : "Modifier le lien"}
        </StyledTitle>

        <Spacer size="1rem" />

        <div>
          Attention : ces liens seront disponibles <strong>publiquement</strong>{" "}
          et tout le monde pourra y accéder. Ne partagez pas de boucles privées.
        </div>

        <Spacer size="1.5rem" />

        <TextField
          id="title"
          name="title"
          label="Titre à afficher"
          helpText="Exemple : « Vidéo de présentation »"
          onChange={handleInputChange}
          value={formData.title}
        />
        <Spacer size="1rem" />

        <TextField
          id="url"
          name="url"
          label="URL"
          onChange={handleInputChange}
          value={formData.url}
        />
        <Spacer size="1rem" />
        <Button color="secondary">
          {NEW_LINK === config ? "Ajouter ce lien" : "Enregistrer"}
        </Button>
      </>
    );
  }

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Liens et réseaux sociaux du groupe</StyledTitle>

      <Spacer size="1rem" />

      {/* {!LINKS?.length && <> */}
      <div>
        Vous n’avez pas encore de lien !
        <Spacer size="0.5rem" />
        Ajoutez vos réseaux sociaux et sites web pour permettre à tout le monde
        de les retrouver facilement
      </div>
      <Spacer size="1rem" />
      <Button color="secondary" onClick={() => setConfig(NEW_LINK)}>
        Ajouter un lien
      </Button>
      {/* </>} */}

      <Spacer size="2rem" />

      {/* {LINKS?.length && <> */}
      <GroupLink
        label="Présentation sur Youtube"
        url="https://actionpopulaire.fr"
        onChange={() => setConfig(EDIT_LINK)}
      />
      <hr />
      <GroupLink
        label="Groupe Facebook"
        url="https://actionpopulaire.fr"
        onChange={() => setConfig(EDIT_LINK)}
      />
      <hr />
      <GroupLink
        label="Boucle Telegram"
        url="https://actionpopulaire.fr"
        onChange={() => setConfig(EDIT_LINK)}
      />
      <hr />
      <a
        href="#"
        onClick={() => setConfig(NEW_LINK)}
        style={{ display: "inline-flex", alignItems: "center" }}
      >
        <RawFeatherIcon
          name="plus"
          width="1rem"
          height="1rem"
          style={{
            height: "1rem",
            marginRight: "1rem",
            display: "inline-block",
            textAlign: "center",
          }}
        />
        Ajouter un lien
      </a>
      {/* </>} */}
    </>
  );
};

export default GroupLinksPage;
