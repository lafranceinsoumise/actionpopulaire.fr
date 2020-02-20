import { hot } from "react-hot-loader/root"; // doit être importé avant React

import axios from "../utils/axios";
import React from "react";
import "react-stepzilla/src/css/main.css";
import { Transition } from "react-transition-group";
import qs from "querystring";

import NavSelect from "../utils/navSelect";

import MultiStepForm from "./MultiStepForm";
import FormStep from "./steps/FormStep";
import ContactStep from "./steps/ContactStep";
import LocationStep from "./steps/LocationStep";

import "./style.css";
import PropTypes from "prop-types";

class CreateGroupForm extends React.Component {
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
        name: "Un groupe pour quoi ?",
        component: (
          <GroupTypeStep
            setFields={this.setFields}
            fields={this.state.fields}
            subtypes={this.props.subtypes}
            types={this.props.types}
          />
        )
      },
      {
        name: "Informations de contact",
        component: (
          <ContactStep setFields={this.setFields} fields={this.state.fields} />
        )
      },
      {
        name: "Localisation",
        component: (
          <LocationStep setFields={this.setFields} fields={this.state.fields} />
        )
      },
      {
        name: "Validation et nom",
        component: (
          <ValidateStep fields={this.state.fields} types={this.props.types} />
        )
      }
    ];

    return <MultiStepForm steps={steps} />;
  }
}
CreateGroupForm.propTypes = {
  initial: PropTypes.object,
  subtypes: PropTypes.array,
  types: PropTypes.array
};

class GroupTypeStep extends FormStep {
  constructor(props) {
    super(props);
    this.groupRefs = props.types.map(() => React.createRef());
  }

  isValidated() {
    const { subtypes } = this.props.fields;
    return !!subtypes && subtypes.length !== 0;
  }

  subtypesFor(type) {
    return this.props.subtypes.filter(s => s.type === type);
  }

  setType(type) {
    return () => {
      if (type !== this.state.type) {
        this.props.setFields({ type, subtypes: [] });
      }
      const subtypes = this.subtypesFor(type);

      if (subtypes.length < 2) {
        this.props.setFields({ type, subtypes: subtypes.map(s => s.label) });
      }
    };
  }

  render() {
    const { fields } = this.props;

    return (
      <div className="row padtopmore">
        <div className="col-sm-6">
          <h4>Quel type de groupe voulez-vous créer ?</h4>
          <blockquote>
            <p>
              &laquo;&nbsp;Chaque insoumis.e peut créer ou rejoindre un ou
              plusieurs groupes d’action dès lors qu’il respecte le cadre et la
              démarche de la France insoumise dans un esprit d’ouverture, de
              bienveillance et de volonté de se projeter dans
              l’action.&nbsp;&raquo;
            </p>
            <footer>
              <a href="https://lafranceinsoumise.fr/groupes-appui/charte-groupes-dappui-de-france-insoumise/">
                Charte des groupes d’action de la France insoumise
              </a>
            </footer>
          </blockquote>
          <p>
            La{" "}
            <a href="https://lafranceinsoumise.fr/groupes-appui/charte-groupes-dappui-de-france-insoumise/">
              Charte des groupes d’action de la France insoumise
            </a>{" "}
            définit quatres types de groupes différents.
          </p>
          <p>
            Ces groupes répondent à des besoins différents. Vous pouvez
            parfaitement participer à plusieurs groupes en fonction de vos
            intérêts.
          </p>
        </div>
        <div className="col-sm-6 padbottom">
          {this.props.types.map((type, i) => (
            <div key={type.id} className="type-selector">
              <button
                className={fields.type === type.id ? "active" : ""}
                style={{ whiteSpace: "normal" }}
                onClick={this.setType(type.id)}
              >
                <h5>{type.label}</h5>
                {type.description}
              </button>
              <Transition
                in={
                  fields.type === type.id &&
                  this.subtypesFor(type.id).length > 1
                }
                timeout={1000}
                mountOnEnter
                unmountOnExit
              >
                {state => {
                  const show =
                    this.groupRefs[i].current &&
                    ["entering", "entered"].includes(state);
                  return (
                    <div
                      className="subtype-selector"
                      ref={this.groupRefs[i]}
                      style={{
                        height: show
                          ? this.groupRefs[i].current.scrollHeight + "px"
                          : "0"
                      }}
                    >
                      <div>
                        <em>
                          Choisissez maintenant les thèmes qui vous intéressent.
                        </em>
                        <NavSelect
                          choices={this.subtypesFor(type.id).map(s => ({
                            value: s.label,
                            label: s.description
                          }))}
                          value={fields.subtypes}
                          max={3}
                          onChange={subtypes =>
                            this.props.setFields({ subtypes })
                          }
                        />
                      </div>
                    </div>
                  );
                }}
              </Transition>
            </div>
          ))}
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
      name: this.groupName.value,
      contact_name: fields.name || null,
      contact_email: fields.email,
      contact_phone: fields.phone,
      contact_hide_phone: fields.hidePhone,
      location_name: fields.locationName,
      location_address1: fields.locationAddress1,
      location_address2: fields.locationAddress2 || null,
      location_zip: fields.locationZip,
      location_city: fields.locationCity,
      location_country: fields.locationCountryCode,
      type: fields.type,
      subtypes: fields.subtypes
    });

    try {
      let res = await axios.post("form/", data);
      location.href = res.data.url;
    } catch (e) {
      this.setState({ error: e, processing: false });
    }
  }

  render() {
    const { fields, types } = this.props;
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées.</p>
          <ul>
            <li>
              <strong>Type de groupe&nbsp;:</strong>{" "}
              {types.find(t => t.id === fields.type).label}
            </li>
            <li>
              <strong>Numéro de téléphone&nbsp;:</strong> {fields.phone} (
              {fields.hidePhone ? "caché" : "public"})
            </li>
            {fields.name && (
              <li>
                <strong>Nom du contact&nbsp;:</strong> {fields.name}
              </li>
            )}
            <li>
              <strong>Adresse email du groupe&nbsp;:</strong> {fields.email}
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
            groupe&nbsp;! Choisissez un nom simple et descriptif (par exemple :
            &laquo;&nbsp;Groupe d'action de la Porte d'Arras&nbsp;&raquo;).
          </p>
          <form onSubmit={this.post}>
            <div className="form-group">
              <input
                className="form-control"
                ref={i => (this.groupName = i)}
                type="text"
                placeholder="Nom du groupe"
                required
              />
            </div>
            <button
              className="btn btn-primary"
              type="submit"
              disabled={this.state.processing}
            >
              Créer mon groupe
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

export default hot(CreateGroupForm);
