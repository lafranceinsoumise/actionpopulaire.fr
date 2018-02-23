import React from 'react';
const countries = require('localized-countries')(require('localized-countries/data/fr'));

import FormStep from './FormStep';

export default class LocationStep extends FormStep {
  constructor(props) {
    super(props);
    this.state.fields = {
      locationName: props.fields.locationName || '',
      locationAddress1: props.fields.locationAddress1 || '',
      locationAddress2: props.fields.locationAddress2 || '',
      locationZip: props.fields.locationZip || '',
      locationCity: props.fields.locationCity || '',
      locationCountryCode: props.fields.locationCountryCode || 'FR',
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();

    this.setFields({
      locationName: this.state.fields.locationName,
      locationAddress1: this.state.fields.locationAddress1,
      locationAddress2: this.state.fields.locationAddress2,
      locationZip: this.state.fields.locationZip,
      locationCity: this.state.fields.locationCity,
      locationCountryCode: this.state.fields.locationCountryCode,
    });
    this.jumpToStep(this.props.step + 1);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <h4>Localisation</h4>
          <p>
            Merci d'indiquer une adresse précise avec numéro de rue, sans quoi le point n'apparaîtra pas sur la carte.
          </p>
          <p>
            S'il s'agit d'une adresse personnelle et que vous ne souhaitez pas la rendre publique, vous
            pouvez indiquer un endroit à proximité, comme un café, ou votre mairie.
          </p>
          {
            this.props.step > 0 &&
            <a className="btn btn-default"
              onClick={() => this.jumpToStep(this.props.step - 1)}>&larr;&nbsp;Précédent</a>
          }
        </div>
        <div className="col-md-6">
          <form onSubmit={this.handleSubmit}>
            <div className="form-group">
              <label>Nom du lieu</label>
              <input
                name="locationName"
                onChange={this.handleInputChange}
                value={this.state.fields.locationName}
                placeholder="Exemple : café de la gare, rue des postes..."
                className="form-control"
                type="text"
                required/>
            </div>
            <div className="form-group">
              <label className="control-label">Adresse</label>
              <input
                name="locationAddress1"
                onChange={this.handleInputChange}
                value={this.state.fields.locationAddress1}
                placeholder="1ère ligne"
                className="form-control"
                type="text"
                required/>
              <input
                name="locationAddress2"
                onChange={this.handleInputChange}
                value={this.state.fields.locationAddress2}
                placeholder="2ème ligne"
                className="form-control"
                type="text"/>
            </div>
            <div className="row">
              <div className="col-md-4">
                <div className="form-group">
                  <label className="control-label">Code postal</label>
                  <input
                    name="locationZip"
                    onChange={this.handleInputChange}
                    value={this.state.fields.locationZip}
                    className="form-control"
                    type="text"
                    required/>
                </div>
              </div>
              <div className="col-md-8">
                <div className="form-group">
                  <label className="control-label">Ville</label>
                  <input
                    name="locationCity"
                    onChange={this.handleInputChange}
                    value={this.state.fields.locationCity}
                    className="form-control"
                    type="text"
                    required/>
                </div>
              </div>
            </div>
            <div className="form-group">
              <label className="control-label">Pays</label>
              <select
                name="locationCountryCode"
                onChange={this.handleInputChange}
                value={this.state.fields.locationCountryCode}
                className="form-control"
                required>
                {countries.array().map(country => (
                  <option value={country.code} key={country.code}>{country.label}</option>))}
              </select>
            </div>
            <button className="btn btn-primary" type="submit">Suivant&nbsp;&rarr;</button>
          </form>
        </div>
      </div>
    );
  }
}
