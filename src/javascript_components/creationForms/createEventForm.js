import axios from '../lib/axios';
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
    label: 'Une réunion de groupe',
    description: 'Une réunion qui concerne principalement les membres du groupes, et non le public de façon générale. ' +
    'Par exemple, la réunion hebdomadaire du groupe, une réunion de travail, ou l\'audition d\'une association'
  },
  {
    id: 'M',
    label: 'Une réunion publique',
    description: 'Une réunion ouverts à tous les publics, au-delà des membres du groupe d\'action, mais qui aura lieu ' +
    'dans un lieu privé. Par exemple, une réunion publique avec un orateur, une projection ou un concert.'
  },
  {
    id: 'A',
    label: 'Une action publique',
    description: 'Une action qui se déroulera dans un lieu public et qui aura comme objectif principal d\'aller à la' +
    'rencontre ou d\'atteindre des personnes extérieures à la FI'
  },
  {
    id: 'O',
    label: 'Un autre type d\'événement',
    description: 'Tout autre type d\'événement qui ne rentre pas dans les catégories ci-dessus.'
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
        component: <EventTypeStep setFields={this.setFields} subtypes={this.state.subtypes} fields={this.state.fields} step={0} />
      },
      {name: 'Qui ?', component: <ContactStep setFields={this.setFields} fields={this.state.fields} step={1} />},
      {name: 'Quand ?', component: <ScheduleStep setFields={this.setFields} fields={this.state.fields} step={2} />},
      {name: 'Où ?', component: <LocationStep setFields={this.setFields} fields={this.state.fields} step={3} />},
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
    this.state.fields.subtype = props.fields.subtype;
    this.setFields = this.setFields.bind(this);
    this.confirm = this.confirm.bind(this);
    this.allSubtypes = props.subtypes;
    this.rankedSubtypes = props.subtypes.reduce((acc, s) => {
      (acc[s.type] = acc[s.type] || []).push(s);
      return acc;
    }, {});
  }

  setSubtype(subtype) {
    this.setState({
      fields: Object.assign(this.state.fields, {
        subtype: subtype,
      })
    });
  }

  confirm(e) {
    e.preventDefault();
    this.setFields({subtype: this.state.fields.subtype});
    this.jumpToStep(1);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-sm-6">
          <h2>Quel type d'événement voulez-vous créer ?</h2>
          <p>
            Chaque insoumis·e peut créer un événement sur la plateforme dès lors
            qu’il respecte le cadre et la démarche de la France insoumise dans un esprit
            d’ouverture, de bienveillance et de volonté de se projeter dans l’action.
          </p>
          <p>
            Afin de mieux identifier les événements que vous créez, et de pouvoir mieux les recommander aux autres
            insoumis⋅es, indiquez le type d'événement que vous organisez.
          </p>
          <p>
            Vous souhaitez inviter une oratrice ou un orateur national&nbsp;? <a href="https://lafranceinsoumise.fr/groupes-appui/inviter-des-intervenants/">Suivez le mode d'emploi.</a>
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
                        <li className={subtype === this.state.fields.subtype ? 'active' : ''} key={subtype.description}>
                          <a href="#" onClick={(e) => {
                            e.preventDefault();
                            this.setSubtype(subtype);
                          }}>
                            <i className={'fa ' + (subtype === this.state.fields.subtype ? 'fa-check-circle' : 'fa-circle-o')}/>
                            &nbsp;
                            {subtype.description}
                          </a>
                        </li>
                      ))
                    }
                  </ul>
                </div>
              ))
            }
            <button className="btn btn-primary" type="submit" disabled={!this.state.fields.subtype}>
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
    this.state = {fields: props.fields, processing: false};
  }

  async post(e) {
    e.preventDefault();
    this.setState({processing: true});

    let data = qs.stringify({
      name: this.eventName.value,
      contact_email: this.state.fields.email,
      contact_name: this.state.fields.name || null,
      contact_phone: this.state.fields.phone,
      contact_hide_phone: this.state.fields.hidePhone,
      start_time: this.state.fields.startTime.format('YYYY-MM-DD HH:mm:SS'),
      end_time: this.state.fields.endTime.format('YYYY-MM-DD HH:mm:SS'),
      location_name: this.state.fields.locationName,
      location_address1: this.state.fields.locationAddress1,
      location_address2: this.state.fields.locationAddress2 || null,
      location_zip: this.state.fields.locationZip,
      location_city: this.state.fields.locationCity,
      location_country: this.state.fields.locationCountryCode,
      subtype: this.state.fields.subtype.label,
      calendar: '1',
      as_group: qs.parse(window.location.search.slice(1)).as_group
    });

    try {
      let res = await axios.post('form/', data);
      location.href = res.data.url;
    } catch (e) {
      this.setState({error: e, processing: false});
    }
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées.</p>
          <ul>
            <li>
              <strong>Type d'événement&nbsp;:</strong> {this.state.fields.subtype.label}
            </li>
            <li>
              <strong>Numéro de
                téléphone&nbsp;:</strong> {this.state.fields.phone} ({this.state.fields.hidePhone === 'on' ? 'caché' : 'public'})
            </li>
            {this.state.fields.name &&
              <li>
                <strong>Nom du contact pour l'événement&nbsp;:</strong> {this.state.fields.name}
              </li>
            }
            <li>
              <strong>Adresse email de contact pour l'événement&nbsp;:</strong> {this.state.fields.email}
            </li>
            <li>
              <strong>Horaires&nbsp;:</strong> Du {this.state.fields.startTime.format('LLL')} au {this.state.fields.endTime.format('LLL')}.
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
            <button className="btn btn-primary" type="submit" disabled={this.state.processing}>Créer mon événement</button>
          </form>
          {this.state.error && (
            <div className="alert alert-warning">
              Une erreur s'est produite. Merci de réessayer plus tard.
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default CreateEventForm;
