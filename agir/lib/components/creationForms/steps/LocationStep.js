import React from "react";

const countries = require("localized-countries/data/fr");
const countriesFirst = ["FR", "PT", "DZ", "MA", "TR", "IT", "GB", "ES"];

const fullCountryList = countriesFirst
  .map((code) => ({ code, label: countries[code], key: `${code}1` }))
  .concat(
    Object.keys(countries)
      .map((code) => ({ code, label: countries[code], key: `${code}2` }))
      .sort(({ label: label1 }, { label: label2 }) =>
        label1.localeCompare(label2),
      ),
  );

import FormStep from "./FormStep";

const requiredFields = [
  "locationName",
  "locationAddress1",
  "locationCity",
  "locationCountryCode",
];

export default class LocationStep extends FormStep {
  constructor(props) {
    props.fields.locationCountryCode = props.fields.locationCountryCode || "FR";
    super(props);
  }

  isValidated() {
    const { fields } = this.props;
    this.resetErrors();

    for (let f of requiredFields) {
      if (!fields[f] || fields[f].trim() === "") {
        this.setError(f, "Ce champ est requis.");
      }
    }

    if (fields.locationCountryCode === "FR") {
      if (!fields.locationZip) {
        this.setError("locationZip", "Ce champ est requis.");
      } else if (!fields.locationZip.match("^[0-9]{5}$")) {
        this.setError("locationZip", "Ce code postal est incorrect.");
      }
    }

    return !this.hasErrors();
  }

  render() {
    const { fields, helpText } = this.props;
    return (
      <div className="row padtopmore padbottommore">
        <div className="col-md-6">
          <h4>Localisation</h4>
          <p>
            Merci d'indiquer une adresse précise avec numéro de rue, sans quoi
            le point n'apparaîtra pas sur la carte.
          </p>
          <p>
            S'il s'agit d'une adresse personnelle et que vous ne souhaitez pas
            la rendre publique, vous pouvez indiquer un endroit à proximité,
            comme un café, ou votre mairie.
          </p>
          {helpText ? <p>{helpText}</p> : null}
        </div>
        <div className="col-md-6">
          <div
            className={
              "form-group" + (this.hasError("locationName") ? " has-error" : "")
            }
          >
            <label>Nom du lieu</label>
            <input
              name="locationName"
              onChange={this.handleInputChange}
              value={fields.locationName || ""}
              placeholder="Exemple : café de la gare, rue des postes..."
              className="form-control"
              type="text"
              required
            />
            {this.showError("locationName")}
          </div>
          <div
            className={
              "form-group" +
              (this.hasError("locationAddress1") ? " has-error" : "")
            }
          >
            <label className="control-label">Adresse</label>
            <input
              name="locationAddress1"
              onChange={this.handleInputChange}
              value={fields.locationAddress1 || ""}
              placeholder="1ère ligne"
              className="form-control"
              type="text"
              required
            />
            <input
              name="locationAddress2"
              onChange={this.handleInputChange}
              value={fields.locationAddress2 || ""}
              placeholder="2ème ligne"
              className="form-control"
              type="text"
            />
            {this.showError("locationAddress1")}
          </div>
          <div className="row">
            <div className="col-md-4">
              <div
                className={
                  "form-group" +
                  (this.hasError("locationZip") ? " has-error" : "")
                }
              >
                <label className="control-label">Code postal</label>
                <input
                  name="locationZip"
                  onChange={this.handleInputChange}
                  value={fields.locationZip || ""}
                  className="form-control"
                  type="text"
                  required
                />
                {this.showError("locationZip")}
              </div>
            </div>
            <div className="col-md-8">
              <div
                className={
                  "form-group" +
                  (this.hasError("locationCity") ? " has-error" : "")
                }
              >
                <label className="control-label">Ville</label>
                <input
                  name="locationCity"
                  onChange={this.handleInputChange}
                  value={fields.locationCity || ""}
                  className="form-control"
                  type="text"
                  required
                />
                {this.showError("locationCity")}
              </div>
            </div>
          </div>
          <div
            className={
              "form-group" +
              (this.hasError("locationCountryCode") ? " has-error" : "")
            }
          >
            <label className="control-label">Pays</label>
            <select
              name="locationCountryCode"
              onChange={this.handleInputChange}
              value={fields.locationCountryCode || ""}
              className="form-control"
              required
            >
              {fullCountryList.map((country) => (
                <option value={country.code} key={country.key}>
                  {country.label}
                </option>
              ))}
            </select>
            {this.showError("locationCountryCode")}
          </div>
        </div>
      </div>
    );
  }
}
