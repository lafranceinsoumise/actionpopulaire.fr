import React from "react";
import Card from "../../../front/components/genericComponents/Card";
import PropTypes from "prop-types";
import { Column, Row } from "../../../front/components/genericComponents/grid";
import Button from "../../../front/components/genericComponents/Button";

const EventDescription = ({
  compteRendu,
  compteRenduPhotos,
  illustration,
  description,
}) => (
  <>
    {compteRendu && (
      <>
        <h2 style={{ fontSize: "20px" }}>Compte-rendu</h2>
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
        <Button href="#" style={{ margin: "16px 0" }}>
          Ajouter une photo
        </Button>
        <div
          dangerouslySetInnerHTML={{ __html: compteRendu }}
          style={{ marginBottom: "60px" }}
        />
      </>
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
};

export default EventDescription;
