import React from 'react';
const countries = require('localized-countries')(require('localized-countries/data/fr'));

import FormStep from './FormStep';

export default class LocationStep extends FormStep {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();

    this.setFields({
      locationName: this.locationName.value,
      locationAddress1: this.locationAddress1.value,
      locationAddress2: this.locationAddress2.value,
      locationZip: this.locationZip.value,
      locationCity: this.locationCity.value,
      locationCountryCode: this.locationCountryCode.value,
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
              <input ref={i => this.locationName = i} placeholder="Exemple: café de la gare, rue des postes..."
                     className="form-control" type="text" required/>
            </div>
            <div className="form-group">
              <label className="control-label">Adresse</label>
              <input ref={i => this.locationAddress1 = i} placeholder="1ère ligne" className="form-control" type="text"
                     required/>
              <input ref={i => this.locationAddress2 = i} placeholder="2ème ligne" className="form-control"
                     type="text"/>
            </div>
            <div className="row">
              <div className="col-md-4">
                <div className="form-group">
                  <label className="control-label">Code postal</label>
                  <input ref={i => this.locationZip = i} className="form-control" type="text" required/>
                </div>
              </div>
              <div className="col-md-8">
                <div className="form-group">
                  <label className="control-label">Ville</label>
                  <input ref={i => this.locationCity = i} className="form-control" type="text" required/>
                </div>
              </div>
            </div>
            <div className="form-group">
              <label className="control-label">Pays</label>
              <select ref={i => this.locationCountryCode = i} className="form-control" required defaultValue='FR'>
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
};