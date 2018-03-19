import React from 'react';
import {PhoneNumberUtil, PhoneNumberFormat} from 'google-libphonenumber';
import Cleave from 'cleave.js/react';
import CleavePhone from 'cleave.js/dist/addons/cleave-phone.fr';


const phoneUtil = PhoneNumberUtil.getInstance();

import FormStep from './FormStep';

class ContactStep extends FormStep {
  constructor(props) {
    super(props);
    this.state.fields = {
      name: props.fields.name || '',
      email: props.fields.email || '',
      phone: props.fields.phone || '',
      hidePhone: props.fields.hidePhone || false,
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();

    let phone = this.state.fields.phone;
    let phoneValid = false;
    try {
      let phoneNumber = phoneUtil.parse(phone, 'FR');
      phoneValid = phoneUtil.isValidNumber(phoneNumber);
      phone = phoneUtil.format(phoneNumber, PhoneNumberFormat.E164);
    } catch (e) {
      phoneValid = false;
    }

    if (!phoneValid) {
      return this.setState({errors: {phone: 'Vous devez entrer un numéro de téléphone valide.'}});
    }

    this.setFields({
      name: this.state.fields.name,
      email: this.state.fields.email,
      phone,
      hidePhone: this.state.fields.hidePhone
    });
    this.jumpToStep(this.props.step + 1);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <h4>Informations de contact</h4>
          <p>
            Ces informations sont les informations de contact. Vous devez indiquer une adresse email et un
            numéro de téléphone. Vous pouvez également préciser le nom d'un·e contact. Ce ne sont pas forcément
            vos informations de contact personnelles&nbsp;: en particulier, l'adresse email peut être créée pour
            l'occasion et être relevée par plusieurs personnes.
          </p>
          <p>
            Vous pouvez ne pas rendre le numéro de téléphone public (surtout si c'est votre numéro personnel).
            Néanmoins, il est obligatoire de le fournir pour que la coordination des groupes d'action puisse vous
            contacter.
          </p>
          {
            this.props.step > 0 &&
            <a className="btn btn-default" onClick={() => this.jumpToStep(this.props.step - 1)}>&larr;&nbsp;Précédent</a>
          }
        </div>
        <div className="col-md-6">
          <form onSubmit={this.handleSubmit}>
            <div className="form-group">
              <label>Nom du contact (facultatif)</label>
              <input className="form-control" name="name" type="text" value={this.state.fields.name} onChange={this.handleInputChange}/>
            </div>
            <div className="form-group">
              <label>Adresse email de contact</label>
              <input className="form-control" name="email" type="email" value={this.state.fields.email} onChange={this.handleInputChange} required/>
            </div>
            <label>Numéro de téléphone du contact</label>
            <div className="row">
              <div className="col-md-6">
                <div className={'form-group' + (this.state.errors.phone ? ' has-error' : '')}>
                  <Cleave
                    options={{phone: true, phoneRegionCode: 'FR'}}
                    className="form-control"
                    name="phone"
                    value={this.state.fields.phone}
                    onChange={this.handleInputChange} />
                  {this.state.errors.phone ? (<span className="help-block">{this.state.errors.phone}</span>) : ''}
                </div>
              </div>
              <div className="col-md-6">
                <div className="checkbox">
                  <label>
                    <input type="checkbox" name="hidePhone" checked={this.state.fields.hidePhone} onChange={this.handleInputChange}/> Ne pas rendre public
                  </label>
                </div>
              </div>
            </div>
            <button className="btn btn-primary" type="submit">Suivant&nbsp;&rarr;</button>
          </form>
        </div>
      </div>
    );
  }
}

export default ContactStep;
