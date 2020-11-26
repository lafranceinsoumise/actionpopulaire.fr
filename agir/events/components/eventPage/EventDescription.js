import React from "react";
import PropTypes from "prop-types";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import { DateTime } from "luxon";
import Button from "@agir/front/genericComponents/Button";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";

const EventDescription = ({
  compteRendu,
  compteRenduPhotos,
  illustration,
  description,
  isOrganizer,
  endTime,
  rsvp,
  routes,
}) => (
  <>
    {(!!compteRendu || compteRenduPhotos.length > 0) && (
      <h2 style={{ fontSize: "20px", marginTop: 0 }}>Compte-rendu</h2>
    )}
    {compteRenduPhotos.length > 0 && (
      <Row gutter={12}>
        {compteRenduPhotos.map((url, key) => (
          <Column collapse={500} key={key} width={["50%", "content"]}>
            <img
              src={url}
              alt="Photo de l'événement postée par l'utilisateur"
            />
          </Column>
        ))}
      </Row>
    )}
    {endTime < DateTime.local() && isOrganizer && (
      <Button
        as="a"
        color="primary"
        href={routes.compteRendu}
        style={{ margin: "1em 1em 0 0" }}
      >
        {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
      </Button>
    )}
    {endTime < DateTime.local() && !!rsvp && (
      <Button as="a" href={routes.addPhoto} style={{ marginTop: "1em" }}>
        Ajouter une photo
      </Button>
    )}
    {compteRendu && (
      <div
        dangerouslySetInnerHTML={{ __html: compteRendu }}
        style={{ margin: "1em 0 3em" }}
        fadingOverflow
      />
    )}
    {description && (
      <h2 style={{ fontSize: "20px", marginTop: 0 }}>L'événement</h2>
    )}
    {illustration && (
      <img
        src={illustration}
        alt="Image d'illustration de l'événement postée par l'utilisateur"
        style={{
          maxWidth: "100%",
          height: "auto",
          maxHeight: "500px",
          marginBottom: "32px",
        }}
      />
    )}
    {description ? (
      <Collapsible
        dangerouslySetInnerHTML={{ __html: description }}
        fadingOverflow
      />
    ) : (
      isOrganizer && (
        <>
          <h2 style={{ fontSize: "20px", marginTop: 0 }}>
            Ajoutez une description !
          </h2>
          <p>
            Donner tous les informations nécessaires aux participants de votre
            événement. Comment accéder au lieu, quel est le programme, les liens
            pour être tenu au courant... Et ajoutez une image !
          </p>
          <Button as="a" color="primary" href={routes.edit}>
            Ajouter une description
          </Button>
        </>
      )
    )}
  </>
);

EventDescription.propTypes = {
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.instanceOf(DateTime),
  routes: PropTypes.object,
  rsvp: PropTypes.string,
};

export default EventDescription;
