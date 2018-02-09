import axios from '../lib/axios';
import 'babel-polyfill';
import React from 'react';
import StepZilla from 'react-stepzilla';
import 'react-stepzilla/src/css/main.css';
import qs from 'querystring';

import FormStep from './steps/FormStep';
import ContactStep from './steps/ContactStep';
import LocationStep from './steps/LocationStep';
import ScheduleStep from './steps/ScheduleStep';

import './style.css';

const apiEndpoint = API_ENDPOINT; // defined by webpack

const groupTypes = [
  {
    id: 'G',
    label: 'Réunion de groupe',
    description: 'Une réunion qui concerne principalement les membres du groupes, et non le public de façon générale. ' +
    'Par exemple, la réunion hebdomadaire du groupe, une réunion de travail, ou l\'audition d\'une association'
  },
  {
    id: 'M',
    label: 'Réunion publique',
    description: 'Une réunion ouverts à tous les publics, au-delà des membres du groupe d\'action, mais qui aura lieu ' +
    'dans un lieu privé. Par exemple, une réunion publique avec un orateur, une projection ou un concert.'
  },
  {
    id: 'A',
    label: 'Action publique',
    description: 'Une action qui se déroulera dans un lieu public et qui '
  }
];

class CreateEventForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {fields: {}};
    this.setFields = this.setFields.bind(this);
  }

  async componentDidMount() {
    let subtypes = (await axios.get(apiEndpoint + '/events_subtypes/')).data;
    this.setState({subtypes});

  }

  setFields(fields) {
    this.setState({fields: Object.assign(this.state.fields, fields)});
  }

  render() {
    if (!this.state.subtypes) {
      return null;
    }

    let steps = [
      {
        name: 'Quel type ?',
        component: <EventTypeStep setFields={this.setFields} subtypes={this.state.subtypes} step={0} />
      },
      {name: 'Qui ?', component: <ContactStep setFields={this.setFields} step={1} />},
      {name: 'Quand ?', component: <ScheduleStep setFields={this.setFields} step={2} />},
      {name: 'Où ?', component: <LocationStep setFields={this.setFields} step={3} />},
      {name: 'Validation et nom', component: <ValidateStep fields={this.state.fields} step={4} />},
    ];

    return (
      <div className="step-progress">
        <StepZilla steps={steps} stepsNavigation={false} showNavigation={false} preventEnterSubmission={true}/>
      </div>
    );
  }
}


class EventTypeStep extends FormStep {
  constructor(props) {
    super(props);
    this.allSubtypes = props.subtypes;
    this.rankedSubtypes = props.subtypes.reduce((acc, s) => {
      (acc[s.type] = acc[s.type] || []).push(s);
      return acc;
    }, {});
    this.confirm = this.confirm.bind(this);
    this.setSubtype = this.setSubtype.bind(this);

    this.setState({subtype: null});
  }

  setSubtype(subtype) {
    this.setState({subtype});
  }

  confirm(e) {
    e.preventDefault();
    this.props.setFields({subtype: this.state.subtype});
    this.jumpToStep(1);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-sm-6">
          <h2>Quel type d'événement voulez-vous créer ?</h2>
          <p>
            Chaque insoumis.e peut créer un événement sur la plateforme dès lors
            qu’il respecte le cadre et la démarche de la France insoumise dans un esprit
            d’ouverture, de bienveillance et de volonté de se projeter dans l’action.
          </p>
          <p>
            Afin de mieux identifier les événements que vous créez, et de pouvoir mieux les recommander aux autres
            insoumis⋅es, indiquez le type d'événement que vous organisez :
          </p>
        </div>
        <div className="col-sm-6 padbottom">
          <h3>Je veux créer...</h3>
          <form onSubmit={(e) => this.confirm(e)}>
            {
              groupTypes.map(type => (
                <div key={type.id}>
                  <h4>{type.label}</h4>
                  <ul className="nav nav-pills">
                    {
                      this.rankedSubtypes[type.id].map(subtype => (
                        <li className={subtype === this.state.subtype ? 'active' : ''} key={subtype.id}>
                          <a href="#" onClick={(e) => {
                            e.preventDefault();
                            this.setSubtype(subtype)
                          }}>
                            <i className={'fa ' + (subtype === this.state.subtype ? 'fa-check-circle' : 'fa-circle-o')}/>
                            &nbsp;
                            {subtype.label}
                          </a>
                        </li>
                      ))
                    }
                  </ul>
                </div>
              ))
            }
            <button className="btn btn-primary" type="submit" disabled={!this.state.subtype}>
              Suivant&nbsp;&rarr;
            </button>
          </form>
        </div>
      </div>
    );
  }
}

class ValidateStep extends FormStep {
  constructor(props) {
    super(props);
    this.post = this.post.bind(this);
    this.state = {fields: props.fields};
  }

  async post(e) {
    e.preventDefault();

    let data = qs.stringify({
      name: this.eventName.value,
      contact_email: this.state.fields.email,
      contact_phone: this.state.fields.phone,
      contact_hide_phone: this.state.fields.hidePhone,
      start_time: this.state.start_time,
      end_time: this.state.end_time,
      location_name: this.state.fields.locationName,
      location_address1: this.state.fields.locationAddress1,
      location_adcress2: this.state.fields.locationAddress2 || null,
      location_zip: this.state.fields.locationZip,
      location_city: this.state.fields.locationCity,
      location_country: this.state.fields.locationCountryCode,
      subtype: this.state.fields.subtype,
    });

    try {
      let res = await axios.post('form/', data);
      location.href = res.data.url;
    } catch (e) {
      this.setState({error: e});
    }
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées.</p>
          <ul>
            <li>
              <strong>Type d'événement&nbsp;:</strong> {this.state.subtype.label}
            </li>
            <li>
              <strong>Numéro de
                téléphone&nbsp;:</strong> {this.state.fields.phone} ({this.state.fields.hidePhone === 'on' ? 'caché' : 'public'})
            </li>
            <li>
              <strong>Adresse email de contact pour l'événement&nbsp;:</strong> {this.state.fields.email}
            </li>
            <li>
              <strong>Horaires&nbsp;:</strong> Du
            </li>
            <li>
              <strong>Lieu&nbsp;:</strong><br/>
              {this.state.fields.locationAddress1}<br/>
              {this.state.fields.locationAddress2 ? <span>{this.state.fields.locationAddress2}<br/></span> : ''}
              {this.state.fields.locationZip}, {this.state.fields.locationCity}
            </li>
          </ul>
          <a className="btn btn-default" onClick={() => this.jumpToStep(2)}>&larr;&nbsp;Précédent</a>
        </div>
        <div className="col-md-6">
          <p>Pour finir, il vous reste juste à choisir un nom pour votre événement&nbsp;! Choisissez un nom simple
            et descriptif (par exemple : &laquo;&nbsp;Porte à porte près du café de la gare&nbsp;&raquo;).</p>
          <form onSubmit={this.post}>
            <div className="form-group">
              <input className="form-control" ref={i => this.eventName = i} type="text" placeholder="Nom de l'événement"
                     required/>
            </div>
            <button className="btn btn-primary" type="submit">Créer mon groupe</button>
          </form>
          {this.state.error && (
            <div className="alert alert-warning">
              Un erreur s'est produite. Merci de réessayer plus tard.
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default CreateEventForm;
