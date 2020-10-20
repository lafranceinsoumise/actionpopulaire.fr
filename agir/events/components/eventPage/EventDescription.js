import React from "react";
import PropTypes from "prop-types";
import { Column, Row } from "@agir/front/genericComponents/grid";
import { DateTime } from "luxon";
import Button from "@agir/front/genericComponents/Button";

const EventDescription = ({
  compteRendu,
  compteRenduPhotos,
  illustration,
  description,
  isOrganizer,
  endTime,
  rsvp,
}) => (
  <>
    {(!!compteRendu || !!compteRenduPhotos) && (
      <h2 style={{ fontSize: "20px" }}>Compte-rendu</h2>
    )}
    {compteRenduPhotos && (
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
    {isOrganizer && (
      <Button color="primary" href="#" style={{ marginTop: "1em" }}>
        {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
      </Button>
    )}
    {endTime > DateTime.local() && !!rsvp && (
      <Button href="#" style={{ marginTop: "1em" }}>
        Ajouter une photo
      </Button>
    )}
    {compteRendu && (
      <div
        dangerouslySetInnerHTML={{ __html: compteRendu }}
        style={{ margin: "1em 0 6em" }}
      />
    )}
    <h2 style={{ fontSize: "20px" }}>L'événement</h2>
    {illustration && (
      <img
        src={illustration}
        alt="Image d'illustration de l'événement postée par l'utilisateur"
        style={{
          width: "100%",
          maxWidth: "500px",
          height: "auto",
          marginBottom: "32px",
        }}
      />
    )}
    <div dangerouslySetInnerHTML={{ __html: description }} />
  </>
);

EventDescription.propTypes = {
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.instanceOf(DateTime),
  rsvp: PropTypes,
};

export default EventDescription;
