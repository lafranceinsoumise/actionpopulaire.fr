import axios from "../utils/axios";
import React from "react";
import "react-stepzilla/src/css/main.css";
import { Transition } from "react-transition-group";
import qs from "querystring-es3";

import NavSelect from "../utils/navSelect";

import MultiStepForm from "./MultiStepForm";
import FormStep from "./steps/FormStep";
import ContactStep from "./steps/ContactStep";
import LocationStep from "./steps/LocationStep";

import "./style.css";
import PropTypes from "prop-types";
import { captureMessage } from "@sentry/react";

class CreateGroupForm extends React.Component {
  constructor(props) {
    super(props);
    this.setFields = this.setFields.bind(this);

    let state = {
      fields: props.initial || {},
      skipType: false,
      types: props.types,
    };

    if (state.types.length === 1 && !state.types[0].disabled) {
      state.fields.type = state.types[0].id;
      const subtypes = this.props.subtypes.filter(
        (s) => s.type === state.types[0].id
      );

      if (subtypes.length < 2) {
        state.fields.subtypes = subtypes.map((s) => s.label);

        state.skipType = true;
      }
    }

    this.state = state;
  }

  setFields(fields) {
    this.setState({ fields: Object.assign({}, this.state.fields, fields) });
  }

  render() {
    let steps = [
      {
        name: "Informations de contact",
        component: (
          <ContactStep setFields={this.setFields} fields={this.state.fields} />
        ),
      },
      {
        name: "Localisation",
        component: (
          <LocationStep setFields={this.setFields} fields={this.state.fields} />
        ),
      },
      {
        name: "Validation et nom",
        component: (
          <ValidateStep fields={this.state.fields} types={this.state.types} />
        ),
      },
    ];

    let typeStep = {
      name: "Un groupe pour quoi ?",
      component: (
        <GroupTypeStep
          setFields={this.setFields}
          fields={this.state.fields}
          subtypes={this.props.subtypes}
          types={this.state.types}
        />
      ),
    };

    if (!this.state.skipType) {
      steps.unshift(typeStep);
    }

    return <MultiStepForm steps={steps} />;
  }
}
CreateGroupForm.propTypes = {
  initial: PropTypes.object,
  subtypes: PropTypes.array,
  types: PropTypes.array,
};

class GroupTypeStep extends FormStep {
  constructor(props) {
    super(props);
    this.groupRefs = props.types.map(() => React.createRef());
    this.state = {
      hasError: false,
    };
  }

  isValidated() {
    const { subtypes } = this.props.fields;
    if (!!subtypes && subtypes.length !== 0) {
      return true;
    } else {
      this.setState({ hasError: true });
      return false;
    }
  }

  subtypesFor(type) {
    return this.props.subtypes.filter((s) => s.type === type);
  }

  setType(type) {
    return () => {
      this.setState({ hasError: false });

      if (type !== this.state.type) {
        this.props.setFields({ type, subtypes: [] });
      }
      const subtypes = this.subtypesFor(type);

      if (subtypes.length < 2) {
        this.props.setFields({ type, subtypes: subtypes.map((s) => s.label) });
      }
    };
  }

  render() {
    const { fields } = this.props;

    return (
      <div className="row padtopmore padbottommore">
        <div className="col-sm-4">
          <h3>Quel type de groupe voulez-vous créer&nbsp;?</h3>
          <p>
            Chaque personne peut créer un groupe local et en rejoindre plusieurs
            dès lors qu'elle respecte le cadre et la démarche qui nous réunit
            autour des propositions de la France insoumie et de la{" "}
            <em>NUPES</em>, dans un esprit d'ouverture, de bienveillance et de
            volonté de se projeter dans l'action.
          </p>
          <p>
            En créant votre groupe, vous vous engagez à respecter{" "}
            <a href="https://infos.actionpopulaire.fr/charte-des-groupes-action-populaire/">
              une charte d'éthique
            </a>{" "}
            dans l'animation du groupe.
          </p>
          <p>
            Ces groupes répondent à des besoins différents. Vous pouvez
            parfaitement participer à plusieurs groupes en fonction de vos
            intérêts. En revanche, vous ne pouvez animer qu'un seul groupe de
            chaque type.
          </p>
        </div>

        <div className="col-sm-8 padbottom type-selectors">
          {this.props.types.map((type) => (
            <div
              key={type.id}
              className="type-selector"
              style={{
                flex: type.fullWidth ? "0 0 100%" : undefined,
              }}
            >
              <button
                className={`btn btn-default ${
                  fields.type === type.id ? "active" : ""
                }`.trim()}
                style={{
                  whiteSpace: "normal",
                  backgroundColor: type.disabled ? "transparent" : undefined,
                  opacity: type.disabled ? ".5" : undefined,
                }}
                onClick={type.disabled ? undefined : this.setType(type.id)}
                disabled={type.disabled}
              >
                <strong>{type.label}</strong>
                {type.description}
                {type.disabled ? (
                  <>
                    <br />
                    <br />
                    {type.disabledDescription}
                  </>
                ) : null}
              </button>
            </div>
          ))}
          {this.props.types.map((type, i) => (
            <Transition
              key={"subtype__" + type.id}
              in={
                fields.type === type.id && this.subtypesFor(type.id).length > 1
              }
              timeout={1000}
              mountOnEnter
              unmountOnExit
              onEntering={() => {
                const subtype = document.querySelector(".subtype-selector");
                if (subtype && subtype.scrollIntoView) {
                  subtype.scrollIntoView({
                    behavior: "smooth",
                  });
                }
              }}
            >
              {(state) => {
                const show =
                  this.groupRefs[i] &&
                  fields.type === type.id &&
                  this.subtypesFor(type.id).length > 1;
                return (
                  <div
                    className="subtype-selector"
                    ref={this.groupRefs[i]}
                    style={{
                      height: show
                        ? "entering" === state
                          ? this.groupRefs[i].current.scrollHeight + "px"
                          : "auto"
                        : "2px",
                    }}
                  >
                    <div>
                      <em>Précisez le type de votre groupe</em>
                      <NavSelect
                        choices={this.subtypesFor(type.id).map((s) => ({
                          value: s.label,
                          label: s.description,
                        }))}
                        value={fields.subtypes || []}
                        max={3}
                        onChange={(subtypes) =>
                          this.props.setFields({ subtypes })
                        }
                      />
                    </div>
                  </div>
                );
              }}
            </Transition>
          ))}
          {this.state.hasError && (
            <div className="alert alert-warning margintopless marginbottomless">
              Veuillez choisir un type de groupe avant de continuer.
            </div>
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
    this.toggleMaySubmit = this.toggleMaySubmit.bind(this);
    this.state = {
      maySubmit: false,
      processing: false,
    };
  }

  toggleMaySubmit(e) {
    this.setState({
      maySubmit: e.target.checked,
    });
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
      subtypes: fields.subtypes,
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
    const groupType = types.find((t) => t.id === fields.type) || {};

    return (
      <div className="row padtopmore padbottommore">
        <div className="col-md-6">
          <p>Voici les informations que vous avez entrées&nbsp;:</p>
          <dl className="well confirmation-data-list">
            <dt>Type&nbsp;:</dt> <dd>{groupType.label}</dd>
            <dt>Numéro de téléphone&nbsp;:</dt>
            <dd>
              {fields.phone}&ensp;
              <small>({fields.hidePhone ? "caché" : "public"})</small>
            </dd>
            {fields.name && (
              <>
                <dt>Nom du contact&nbsp;:</dt>
                <dd>{fields.name}</dd>
              </>
            )}
            <dt>Adresse email&nbsp;:</dt>
            <dd>{fields.email}</dd>
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
            groupe&nbsp;! Choisissez un nom simple et descriptif (par exemple :
            &laquo;&nbsp;Groupe d'action de la Porte d'Arras&nbsp;&raquo;).
          </p>
          <form onSubmit={this.post}>
            <div className="form-group">
              <input
                className="form-control"
                ref={(i) => (this.groupName = i)}
                type="text"
                placeholder="Nom du groupe"
                required
              />
            </div>
            <button
              className="btn btn-primary btn-lg btn-block"
              type="submit"
              disabled={!this.state.maySubmit || this.state.processing}
            >
              Créer mon groupe
            </button>
          </form>
          <form>
            <div className="checkbox">
              <label>
                <input onChange={this.toggleMaySubmit} type="checkbox" />
                Je m'engage à respecter{" "}
                <a
                  href="https://infos.actionpopulaire.fr/charte-des-groupes-action-populaire/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  la charte des groupes d'action
                </a>
              </label>
            </div>
          </form>
          {this.state.error && (
            <div className="alert alert-warning margintopless">
              {this.state.error.response.status === 400 &&
              this.state.error.response.data.errors ? (
                <ul>
                  {Object.entries(this.state.error.response.data.errors).map(
                    ([field, msg]) => {
                      captureMessage(`ValidationError: ${field} ${msg}`);
                      return <li key={field}>{msg}</li>;
                    }
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

export default CreateGroupForm;
