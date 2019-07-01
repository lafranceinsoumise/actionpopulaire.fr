import axios from "@agir/lib/utils/axios";
import React from "react";
import PropTypes from "prop-types";
import "react-stepzilla/src/css/main.css";
import qs from "querystring";
import { hot } from "react-hot-loader";

import MultiStepForm from "./MultiStepForm";
import Question from "./Question";
import FormStep from "./steps/FormStep";
import ContactStep from "./steps/ContactStep";
import LocationStep from "./steps/LocationStep";
import ScheduleStep from "./steps/ScheduleStep";

import "./style.css";
import { Spring } from "react-spring/renderprops";

import styled from "styled-components";

class CreateEventForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { fields: props.initial || {} };
    this.setFields = this.setFields.bind(this);
  }

  setFields(fields) {
    this.setState({ fields: Object.assign({}, this.state.fields, fields) });
  }

  hasGroupStep() {
    return this.props.groups && this.props.groups.length > 0;
  }

  render() {
    let steps = [
      {
        name: "Quel type ?",
        component: (
          <EventTypeStep
            setFields={this.setFields}
            fields={this.state.fields}
            types={this.props.types}
            subtypes={this.props.subtypes}
          />
        )
      },
      {
        name: "Questions légales",
        component: (
          <LegalQuestionsStep
            setFields={this.setFields}
            fields={this.state.fields}
            subtypes={this.props.subtypes}
            questions={this.props.questions}
            nextStep={this.hasGroupStep() ? 3 : 2}
          />
        )
      },
      {
        name: "Qui contacter ?",
        component: (
          <ContactStep setFields={this.setFields} fields={this.state.fields} />
        )
      },
      {
        name: "Quand ?",
        component: (
          <ScheduleStep setFields={this.setFields} fields={this.state.fields} />
        )
      },
      {
        name: "Où ?",
        component: (
          <LocationStep setFields={this.setFields} fields={this.state.fields} />
        )
      },
      {
        name: "Validation et nom",
        component: (
          <ValidateStep
            fields={this.state.fields}
            subtypes={this.props.subtypes}
          />
        )
      }
    ];

    if (this.hasGroupStep()) {
      steps.splice(1, 0, {
        name: "Qui organise ?",
        component: (
          <OrganizerStep
            setFields={this.setFields}
            fields={this.state.fields}
            groups={this.props.groups}
          />
        )
      });
    }

    return (
      <MultiStepForm
        steps={steps}
        startAtStep={this.props.initial && this.props.initial.subtype ? 1 : 0}
      />
    );
  }
}

CreateEventForm.propTypes = {
  groups: PropTypes.array,
  initial: PropTypes.object,
  types: PropTypes.array,
  subtypes: PropTypes.array,
  questions: PropTypes.array
};

function CheckBoxList({ children }) {
  return <ul className="nav nav-pills">{children}</ul>;
}

CheckBoxList.propTypes = {
  children: PropTypes.node
};

const GreyedNavPill = styled.a`
  background-color: #f7f7f7;
`;

const Icon = styled.i`
  width: 25px;
  font-size: 16px;
  line-height: 25px;
  border-radius: 25px;
  background-color: #fff;
  text-align: center;
  margin-right: 0.4em;
`;

function CheckBox({ label, active, onClick, icon, iconName, color }) {
  return (
    <li className={active ? "active" : ""}>
      <GreyedNavPill
        href="#"
        onClick={e => {
          e.preventDefault();
          onClick();
        }}
      >
        {icon ? (
          <img src={icon} />
        ) : (
          <Icon style={{ color }} className={"fa fa-" + iconName} />
        )}
        &nbsp;
        {label}
      </GreyedNavPill>
    </li>
  );
}

CheckBox.propTypes = {
  label: PropTypes.string,
  active: PropTypes.bool,
  onClick: PropTypes.func,
  icon: PropTypes.string,
  iconName: PropTypes.string,
  color: PropTypes.string
};

class EventTypeStep extends FormStep {
  constructor(props) {
    super(props);
  }

  setSubtype(subtype) {
    this.props.setFields({
      subtype: subtype.label
    });
  }

  isCurrentSubtype(subtype) {
    return subtype.label === this.props.fields.subtype;
  }

  isValidated() {
    return !!this.props.fields.subtype;
  }

  render() {
    const rankedSubtypes = this.props.subtypes.reduce((acc, s) => {
      (acc[s.type] = acc[s.type] || []).push(s);
      return acc;
    }, {});

    return (
      <div className="row padtopmore">
        <div className="col-sm-6">
          <h2>Quel type d'événement voulez-vous créer ?</h2>
          <p>
            Chaque insoumis·e peut créer un événement sur la plateforme dès lors
            qu’il respecte le cadre et la démarche de la France insoumise dans
            un esprit d’ouverture, de bienveillance et de volonté de se projeter
            dans l’action.
          </p>
          <p>
            Afin de mieux identifier les événements que vous créez, et de
            pouvoir mieux les recommander aux autres insoumis⋅es, indiquez le
            type d'événement que vous organisez.
          </p>
          <p>
            Vous souhaitez inviter un⋅e député⋅e, candidat⋅e, ou animateur⋅ice
            de livret&nbsp;?{" "}
            <a href="https://lafranceinsoumise.fr/groupes-appui/inviter-des-intervenants/">
              Suivez le mode d'emploi.
            </a>
          </p>
        </div>
        <div className="col-sm-6 padbottom">
          <h3>Je veux créer...</h3>
          {this.props.types.map(type => (
            <div key={type.id}>
              <h4>{type.label}</h4>
              <CheckBoxList>
                {rankedSubtypes[type.id].map(subtype => (
                  <CheckBox
                    key={subtype.description}
                    active={this.isCurrentSubtype(subtype)}
                    label={subtype.description}
                    onClick={() => this.setSubtype(subtype)}
                    icon={subtype.icon}
                    iconName={subtype.iconName}
                    color={subtype.color}
                  />
                ))}
              </CheckBoxList>
            </div>
          ))}
        </div>
      </div>
    );
  }
}

class LegalQuestionsStep extends FormStep {
  constructor(props) {
    super(props);
    this.state = { question: 0 };
  }

  getAnswer(id) {
    const legal = this.props.fields.legal || {};
    if (legal.hasOwnProperty(id)) {
      return legal[id];
    }
    return null;
  }

  getQuestions() {
    const subtype = this.props.subtypes.find(
      s => s.label === this.props.fields.subtype
    );
    return this.props.questions.filter(
      q =>
        (!q.type || q.type.includes(subtype.type)) &&
        (!q.when || this.getAnswer(q.when)) &&
        (!q.notWhen || !this.getAnswer(q.notWhen))
    );
  }

  setAnswer(id, value) {
    this.props.setFields({
      legal: Object.assign({}, this.props.fields.legal || {}, {
        [id]: value
      })
    });

    if (this.state.question >= this.getQuestions().length - 1) {
      return this.props.jumpToStep(this.props.nextStep);
    }
    this.setState({ question: this.state.question + 1 });
  }

  isValidated() {
    return this.getQuestions().every(q => this.getAnswer(q.id) !== null);
  }

  render() {
    let q = this.getQuestions()[this.state.question];
    return (
      <div className="row padtopmore">
        <div className="col-sm-6 padbottom">
          <div className="alert alert-danger">
            Attention&nbsp;! Vous ne pouvez engager de frais sans la validation
            de l'équipe de suivi des questions financières de La France
            insoumise. Pour bien identifier la situation légale dans laquelle
            vous vous trouvez, merci de bien vouloir répondre à ces quelques
            questions.
          </div>
        </div>
        <div className="col-sm-6 padbottom">
          <Spring key={q.id} from={{ opacity: 0 }} to={{ opacity: 1 }}>
            {props => (
              <Question
                style={props}
                key={q.id}
                question={q}
                value={this.getAnswer(q.id)}
                setValue={v => this.setAnswer(q.id, v)}
              />
            )}
          </Spring>
        </div>
      </div>
    );
  }
}

class OrganizerStep extends FormStep {
  constructor(props) {
    super(props);
    this.setIndividual = this.setIndividual.bind(this);
  }

  setIndividual() {
    this.props.setFields({ organizerGroup: null });
  }

  setGroup(group) {
    this.props.setFields({ organizerGroup: group.id });
  }

  render() {
    const { organizerGroup } = this.props.fields;

    return (
      <div className="row padtopmore">
        <div className="col-sm-6">
          <h2>Qui organise l'événement ?</h2>
          <p>
            Un événement peut être organisé à titre individuel par une personne.
            Mais comme vous êtes aussi gestionnaire d'un groupe d'action, il est
            aussi possible d'indiquer que cet événement est organisé par votre
            groupe.
          </p>
        </div>
        <div className="col-md-6">
          <h3>L'événement est organisé...</h3>
          <div>
            <h4>...à titre individuel</h4>
            <CheckBoxList>
              <CheckBox
                active={!organizerGroup}
                label="J'en suis l'organisateur"
                onClick={this.setIndividual}
              />
            </CheckBoxList>
          </div>
          <div>
            <h4>...par un groupe d'action</h4>
            <CheckBoxList>
              {this.props.groups.map(group => (
                <CheckBox
                  key={group.id}
                  active={group.id === organizerGroup}
                  label={group.name}
                  onClick={() => this.setGroup(group)}
                />
              ))}
            </CheckBoxList>
          </div>
        </div>
      </div>
    );
  }
}

class ValidateStep extends FormStep {
  constructor(props) {
    super(props);
    this.post = this.post.bind(this);
    this.state = { processing: false };
  }

  async post(e) {
    e.preventDefault();
    this.setState({ processing: true });

    const { fields } = this.props;
    let data = qs.stringify({
      name: this.eventName.value,
      contact_email: fields.email,
      contact_name: fields.name || null,
      contact_phone: fields.phone,
      contact_hide_phone: fields.hidePhone,
      start_time: fields.startTime.format("YYYY-MM-DD HH:mm:SS"),
      end_time: fields.endTime.format("YYYY-MM-DD HH:mm:SS"),
      location_name: fields.locationName,
      location_address1: fields.locationAddress1,
      location_address2: fields.locationAddress2 || null,
      location_zip: fields.locationZip,
      location_city: fields.locationCity,
      location_country: fields.locationCountryCode,
      subtype: fields.subtype,
      as_group: fields.organizerGroup,
      legal: JSON.stringify(fields.legal)
    });

    try {
      let res = await axios.post("form/", data);
      location.href = res.data.url;
    } catch (e) {
      this.setState({ error: e, processing: false });
    }
  }

  getSubtypeDescription() {
    return this.props.subtypes.find(s => s.label === this.props.fields.subtype)
      .description;
  }

  render() {
    const { fields } = this.props;
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées.</p>
          <ul>
            <li>
              <strong>Type d'événement&nbsp;:</strong>{" "}
              {this.getSubtypeDescription()}
            </li>
            <li>
              <strong>Numéro de téléphone&nbsp;:</strong> {fields.phone} (
              {fields.hidePhone ? "caché" : "public"})
            </li>
            {fields.name && (
              <li>
                <strong>Nom du contact pour l'événement&nbsp;:</strong>{" "}
                {fields.name}
              </li>
            )}
            <li>
              <strong>Adresse email de contact pour l'événement&nbsp;:</strong>{" "}
              {fields.email}
            </li>
            <li>
              <strong>Horaires&nbsp;:</strong> Du{" "}
              {fields.startTime.format("LLL")} au {fields.endTime.format("LLL")}
              .
            </li>
            <li>
              <strong>Lieu&nbsp;:</strong>
              <br />
              {fields.locationAddress1}
              <br />
              {fields.locationAddress2 ? (
                <span>
                  {fields.locationAddress2}
                  <br />
                </span>
              ) : (
                ""
              )}
              {fields.locationZip}, {fields.locationCity}
            </li>
          </ul>
        </div>
        <div className="col-md-6">
          <p>
            Pour finir, il vous reste juste à choisir un nom pour votre
            événement&nbsp;! Choisissez un nom simple et descriptif (par exemple
            : &laquo;&nbsp;Porte à porte près du café de la gare&nbsp;&raquo;).
          </p>
          <form onSubmit={this.post}>
            <div className="form-group">
              <input
                className="form-control"
                ref={i => (this.eventName = i)}
                type="text"
                placeholder="Nom de l'événement"
                required
              />
            </div>
            <button
              className="btn btn-primary"
              type="submit"
              disabled={this.state.processing}
            >
              Créer mon événement
            </button>
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

export default hot(module)(CreateEventForm);
