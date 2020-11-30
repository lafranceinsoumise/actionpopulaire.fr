import { hot } from "react-hot-loader/root"; // doit être importé avant React

import axios from "@agir/lib/utils/axios";
import React from "react";
import PropTypes from "prop-types";
import "react-stepzilla/src/css/main.css";
import qs from "querystring";

import MultiStepForm from "./MultiStepForm";
import Question from "./Question";
import FormStep from "./steps/FormStep";
import ContactStep from "./steps/ContactStep";
import LocationStep from "./steps/LocationStep";
import ScheduleStep from "./steps/ScheduleStep";

import "./style.css";
import { Spring } from "react-spring/renderprops";

import styled from "styled-components";
import moment from "moment";

class CreateEventForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { fields: props.initial || {} };
    this.setFields = this.setFields.bind(this);
  }

  setFields(fields) {
    this.setState({ fields: Object.assign({}, this.state.fields, fields) });
  }

  render() {
    let steps = [
      {
        name: "Qui organise ?",
        component: (
          <OrganizerStep
            setFields={this.setFields}
            fields={this.state.fields}
            groups={this.props.groups}
            is2022={this.props.is2022}
            isInsoumise={this.props.isInsoumise}
          />
        ),
      },
      {
        name: "Quel type ?",
        component: (
          <EventTypeStep
            setFields={this.setFields}
            fields={this.state.fields}
            types={this.props.types}
            subtypes={this.props.subtypes}
          />
        ),
      },
      {
        name: "Qui contacter ?",
        component: (
          <ContactStep setFields={this.setFields} fields={this.state.fields} />
        ),
      },
      {
        name: "Quand ?",
        component: (
          <ScheduleStep setFields={this.setFields} fields={this.state.fields} />
        ),
      },
      {
        name: "Où ?",
        component: (
          <LocationStep setFields={this.setFields} fields={this.state.fields} />
        ),
      },
      {
        name: "Validation et nom",
        component: (
          <ValidateStep
            fields={this.state.fields}
            subtypes={this.props.subtypes}
          />
        ),
      },
    ];

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
  is2022: PropTypes.bool,
  isInsoumise: PropTypes.bool,
};

function SubtypeSelector({ children }) {
  return <ul className="nav nav-pills">{children}</ul>;
}

SubtypeSelector.propTypes = {
  children: PropTypes.node,
};

const Icon = styled.i`
  width: 25px;
  font-size: 16px;
  line-height: 25px;
  border-radius: 25px;
  background-color: #fff;
  text-align: center;
  margin-right: 0.4em;
  box-sizing: content-box;
  ${(props) =>
    props.active
      ? "border: 1px solid rgba(10, 10, 10, 0.3);"
      : "border: 1px solid transparent;"}
`;

function CheckBox({
  label,
  active,
  onClick,
  icon,
  iconName,
  color,
  className,
}) {
  return (
    <li className={`${className} ${active ? "active" : ""}`.trim()}>
      <a
        href="#"
        onClick={(e) => {
          e.preventDefault();
          onClick();
        }}
        style={{ whiteSpace: "nowrap" }}
      >
        {icon ? (
          <img src={icon} />
        ) : (
          <Icon
            active={active}
            style={{ color }}
            className={"fa fa-" + iconName}
          />
        )}
        {label}
      </a>
    </li>
  );
}

CheckBox.propTypes = {
  label: PropTypes.string,
  active: PropTypes.bool,
  onClick: PropTypes.func,
  icon: PropTypes.string,
  iconName: PropTypes.string,
  color: PropTypes.string,
  className: PropTypes.string,
};

class EventTypeStep extends FormStep {
  constructor(props) {
    super(props);
  }

  setSubtype(subtype) {
    this.props.setFields({
      subtype: subtype.label,
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
      <div className="row padtopmore padbottommore">
        <div className="col-sm-6">
          <h3>Quel type d'événement voulez-vous créer ?</h3>
          <p>
            Afin de mieux identifier les événements que vous créez, et de
            pouvoir mieux les recommander aux autres membres de la plateforme,
            indiquez le type d'événement que vous organisez.
          </p>
        </div>
        <div className="col-sm-6 padbottom">
          <h3>Je veux créer...</h3>
          {this.props.types.map((type) => (
            <div key={type.id}>
              <h4>{type.label}</h4>
              <SubtypeSelector>
                {rankedSubtypes[type.id].map((subtype) => (
                  <CheckBox
                    key={subtype.description}
                    active={this.isCurrentSubtype(subtype)}
                    label={subtype.description}
                    onClick={() => this.setSubtype(subtype)}
                    icon={subtype.icon}
                    iconName={subtype.iconName}
                    color={subtype.color}
                    className="subtype-selector-choice"
                  />
                ))}
              </SubtypeSelector>
            </div>
          ))}
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

  setIndividual(forUsers) {
    this.props.setFields({ organizerGroup: null, forUsers });
  }

  setGroup(group) {
    this.props.setFields({
      organizerGroup: group.id,
      forUsers: group.forUsers,
    });
  }

  render() {
    const { organizerGroup, forUsers } = this.props.fields;

    let defaultForUsers;
    if (this.props.isInsoumise && !this.props.is2022) {
      defaultForUsers = "I";
    } else if (this.props.is2022 && !this.props.isInsoumise) {
      defaultForUsers = "2";
    }

    if (this.props.groups.length === 0 && defaultForUsers === "2") {
      this.setIndividual(defaultForUsers);
      this.props.jumpToStep(1);
    }

    return (
      <div className="row padtopmore padbottommore">
        <div className="col-sm-6">
          <h2>Qui organise l'événement ?</h2>
          <p>
            Un événement peut être organisé à titre individuel. Mais comme vous
            êtes aussi gestionnaire d'un groupe, il est aussi possible
            d'indiquer que cet événement est organisé par votre groupe.
          </p>
        </div>
        <div className="col-md-6">
          <h3>L'événement est organisé</h3>
          {this.props.groups.length > 0 && (
            <>
              <h4>par un groupe d'action</h4>
              <SubtypeSelector>
                {this.props.groups.map((group) => (
                  <CheckBox
                    iconName={group.iconName}
                    color={group.color}
                    key={group.id}
                    active={group.id === organizerGroup}
                    label={group.name}
                    onClick={() => this.setGroup(group)}
                  />
                ))}
              </SubtypeSelector>
              <h4>à titre individuel</h4>
            </>
          )}
          <SubtypeSelector>
            {this.props.is2022 && this.props.isInsoumise ? (
              <>
                <CheckBox
                  iconName="user"
                  color="#0098b6"
                  active={!organizerGroup && forUsers === "I"}
                  label="pour la France insoumise"
                  onClick={() => this.setIndividual("I")}
                />
                <CheckBox
                  iconName="user"
                  color="#571AFF"
                  active={!organizerGroup && forUsers === "2"}
                  label="pour la campagne « Nous Sommes Pour ! »"
                  onClick={() => this.setIndividual("2")}
                />
              </>
            ) : (
              <>
                <CheckBox
                  iconName="user"
                  color="#0098b6"
                  active={!organizerGroup}
                  label={
                    defaultForUsers === "I"
                      ? "pour la France insoumise"
                      : "pour la campagne « Nous Sommes Pour ! »"
                  }
                  onClick={() => this.setIndividual(defaultForUsers)}
                />
              </>
            )}
          </SubtypeSelector>
          {defaultForUsers === "I" && (
            <p>
              Pour organiser des événements « Nous Sommes Pour ! », vous devez
              d'abord parrainer la candidature sur{" "}
              <a href="https://noussommespour.fr">noussommespour.fr</a>.
            </p>
          )}
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
      for_users: fields.forUsers,
      legal: JSON.stringify(fields.legal || {}),
    });

    try {
      let res = await axios.post("form/", data);
      location.href = res.data.url;
    } catch (e) {
      this.setState({ error: e, processing: false });
    }
  }

  getSubtypeDescription() {
    return this.props.subtypes.find(
      (s) => s.label === this.props.fields.subtype
    ).description;
  }

  render() {
    const { fields } = this.props;
    return (
      <div className="row padtopmore padbottommore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées.</p>
          <dl className="well confirmation-data-list">
            <dt>Type d'événement&nbsp;:</dt>
            <dd>{this.getSubtypeDescription()}</dd>
            <dt>Numéro de téléphone&nbsp;:</dt>
            <dd>
              {fields.phone}&ensp;
              <small>({fields.hidePhone ? "caché" : "public"})</small>
            </dd>
            {fields.name && (
              <>
                <dt>Nom du contact pour l'événement&nbsp;:</dt>{" "}
                <dd>{fields.name}</dd>
              </>
            )}
            <dt>Adresse email de contact pour l'événement&nbsp;:</dt>{" "}
            <dd>{fields.email}</dd>
            <dt>Horaires&nbsp;:</dt>
            <dd>
              du {fields.startTime.format("LLL")} au{" "}
              {fields.endTime.format("LLL")}
            </dd>
            {fields.startTime.isBefore(moment()) && (
              <p className="alert alert-w*arning margintop">
                Attention&nbsp;! Vous avez indiqué une date dans le passé pour
                votre événement. Cela est possible pour rencenser des événements
                passés sur la plateforme, mais personne ne pourra le rejoindre.
              </p>
            )}
            <dt>Lieu&nbsp;:</dt>
            <dd>{fields.locationAddress1}</dd>
            {fields.locationAddress2 ? (
              <dd>{fields.locationAddress2}</dd>
            ) : null}
            <dd>
              {fields.locationZip}, {fields.locationCity}
            </dd>
          </dl>
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
                ref={(i) => (this.eventName = i)}
                type="text"
                placeholder="Nom de l'événement"
                required
              />
            </div>
            <button
              className="btn btn-primary btn-lg btn-block"
              type="submit"
              disabled={this.state.processing}
            >
              Créer mon événement
            </button>
          </form>
          {this.state.error && (
            <div className="alert alert-warning margintopless">
              {this.state.error.response.status === 400 &&
              this.state.error.response.data.errors ? (
                <ul>
                  {Object.entries(this.state.error.response.data.errors).map(
                    ([field, msg]) => (
                      <li key={field}>{msg}</li>
                    )
                  )}
                </ul>
              ) : (
                "Une erreur s'est produite. Merci de réessayer plus tard."
              )}
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default hot(CreateEventForm);
