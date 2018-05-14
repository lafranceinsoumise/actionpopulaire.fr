import React from 'react';
import {PhoneNumberUtil, PhoneNumberFormat} from 'google-libphonenumber';
import Cleave from 'cleave.js/react';
import 'cleave.js/dist/addons/cleave-phone.fr';


const phoneUtil = PhoneNumberUtil.getInstance();

import FormStep from './FormStep';

class ContactStep extends FormStep {
  constructor(props) {
    super(props);
    this.emailInputRef = React.createRef();
  }

  isValidated() {
    // shortcircuit-less and
    return [this.validateName(), this.validateEmail(), this.validatePhone()].every(c => c);
  }

  validateName() {
    const {name} = this.props.fields;
    if (!name || name === '') {
      this.setError('name', 'Vous devez indiquer un nom de contact.');
      return false;
    }

    this.clearError('name');
    return true;
  }

  validateEmail() {
    const {email} = this.props.fields;

    if (!email || email === '') {
      this.setError('email', 'Vous devez indiquer une adresse email de contact pour les personnes qui souhaiteraient' +
        ' se renseigner sur votre groupe');
      return false;
    }

    if (!this.emailInputRef.current.validity.valid) {
      this.setError('email', 'Cette adresse email n\'est pas valide.');
      return false;
    }

    this.clearError('email');
    return true;
  }

  validatePhone() {
    const {phone} = this.props.fields;

    if (!phone || phone === '') {
      this.setError('phone', 'Vous devez indiquer un numéro de téléphone.');
      return false;
    }

    let phoneNumber;

    try {
      phoneNumber = phoneUtil.parse(phone, 'FR');
    }
    catch (e) {
      this.setError('phone', 'Ce numéro de téléphone n\'est pas valide');
      return false;
    }

    if (!phoneUtil.isValidNumber(phoneNumber)) {
      this.setError('phone', 'Ce numéro de téléphone n\'est pas valide');
      return false;
    }

    this.clearError('phone');
    return true;
  }

  render() {
    const {name, email, phone, hidePhone} = this.props.fields;
    const {errors} = this.state;

    return (
      <div className="row padtopmore">
        <div className={'col-md-6' + (this.hasErrors() ? ' has-error' : '')}>
          <h4>Informations de contact</h4>
          <p>
            Ces informations sont les informations de contact. Vous devez indiquer une adresse email et un
            numéro de téléphone. Vous pouvez également préciser le nom d'un·e contact. Ce ne sont pas forcément
            vos informations de contact personnelles&nbsp;: en particulier, l'adresse email peut être créée pour
            l'occasion et être relevée par plusieurs personnes.
          </p>
          <p className={errors.phone ? 'help-block' : ''}>
            Vous pouvez ne pas rendre le numéro de téléphone public (surtout si c'est votre numéro personnel).
            Néanmoins, il est obligatoire de le fournir pour que la coordination des groupes d'action puisse vous
            contacter.
          </p>
        </div>
        <div className="col-md-6">
          <div className={'form-group' + (errors.name ? ' has-error' : '')}>
            <label>Nom du contact (facultatif)</label>
            <input
              className="form-control" name="name" type="text" value={name || ''}
              onChange={this.handleInputChange}
            />
            {this.showError('name')}
          </div>
          <div className={'form-group' + (errors.email ? ' has-error' : '')}>
            <label>Adresse email de contact</label>
            <input
              className="form-control" name="email" type="email" value={email || ''}
              onChange={this.handleInputChange} required ref={this.emailInputRef}
            />
            {this.showError('email')}
          </div>
          <label>Numéro de téléphone du contact</label>
          <div className="row">
            <div className="col-md-6">
              <div className={'form-group' + (errors.phone ? ' has-error' : '')}>
                <Cleave
                  options={{phone: true, phoneRegionCode: 'FR'}}
                  className="form-control"
                  name="phone"
                  value={phone || ''}
                  onChange={this.handleInputChange}
                />
                {this.showError('phone')}
              </div>
            </div>
            <div className="col-md-6">
              <div className="checkbox">
                <label>
                  <input
                    type="checkbox" name="hidePhone" checked={hidePhone || false}
                    onChange={this.handleInputChange}
                  /> Ne pas rendre public
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default ContactStep;
