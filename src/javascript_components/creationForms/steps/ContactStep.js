import React from 'react';
import {PhoneNumberUtil, PhoneNumberFormat} from 'google-libphonenumber';
import Cleave from 'cleave.js/react';
import CleavePhone from 'cleave.js/dist/addons/cleave-phone.fr';


const phoneUtil = PhoneNumberUtil.getInstance();

import FormStep from './FormStep';

class ContactStep extends FormStep {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();

    let phone = this.phone.value;
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

    this.setFields({phone, email: this.email.value, hidePhone: this.hidePhone.value});
    this.jumpToStep(this.props.step + 1);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <h4>Informations de contact</h4>
          <p>
            Ces informations sont les informations de contact du groupe. Vous devez indiquer une adresse email et un
            numéro de téléphone. Ce ne sont pas forcément vos informations de contact personnelles&nbsp;: en
            particulier, l'adresse email peut appartenir au groupe et être relevée par plusieurs personnes.
          </p>
          <p>
            Vous pouvez ne pas rendre le numéro de téléphone public (surtout si c'est votre numéro personnel).
            Néanmoins, il est obligatoire de le fournir pour que la coordination des groupes d'action puisse vous
            contacter.
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
              <label>Adresse email du groupe</label>
              <input className="form-control" ref={i => this.email = i} type="email"/>
            </div>
            <label>Numéro de téléphone du contact</label>
            <div className="row">
              <div className="col-md-6">
                <div className={'form-group' + (this.state.errors.phone ? ' has-error' : '')}>
                  <Cleave options={{phone: true, phoneRegionCode: 'FR'}} htmlRef={(i => this.phone = i)} className="form-control"/>
                  {this.state.errors.phone ? (<span className="help-block">{this.state.errors.phone}</span>) : ''}
                </div>
              </div>
              <div className="col-md-6">
                <div className="checkbox">
                  <label>
                    <input ref={i => this.hidePhone = i} type="checkbox"/> Ne pas rendre public
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