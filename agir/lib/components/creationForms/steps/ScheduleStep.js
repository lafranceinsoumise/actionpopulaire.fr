import React from "react";
import Datetime from "react-datetime";
import "moment/locale/fr";

import "react-datetime/css/react-datetime.css";

import FormStep from "./FormStep";

export default class ScheduleStep extends FormStep {
  constructor(props) {
    super(props);
  }

  isValidated() {
    const { startTime, endTime } = this.props.fields;

    this.resetErrors();

    if (!startTime) {
      this.setError("startTime", "Vous devez indiquez une date de début");
    }

    if (!endTime) {
      this.setError("endTime", "Vous devez indiquer une date de fin");
    } else if (startTime && startTime.isAfter(endTime)) {
      this.setError(
        "endTime",
        "Votre événement ferait mieux de finir après avoir commencé !",
      );
    }

    return !this.hasErrors();
  }

  render() {
    const { fields } = this.props;
    return (
      <div className="row padtopmore padbottommore">
        <div className="col-md-6">
          <h4>Calendrier</h4>
          <p>
            Merci de nous indiquer quand aura lieu et combien de temps durera
            votre événement.
          </p>
        </div>
        <div className="col-md-6">
          <form onSubmit={this.handleSubmit}>
            <div
              className={
                "form-group" + (this.hasError("startTime") ? " has-error" : "")
              }
            >
              <label className="control-label">Début de l'événement</label>
              <Datetime
                locale="fr"
                onChange={this.setField("startTime")}
                value={fields.startTime}
              />
              {this.showError("startTime")}
            </div>
            <div
              className={
                "form-group" + (this.hasError("endTime") ? " has-error" : "")
              }
            >
              <label className="control-label">Fin de l'événement</label>
              <Datetime
                locale="fr"
                onChange={this.setField("endTime")}
                value={fields.endTime}
              />
              {this.showError("endTime")}
            </div>
            {this.state.error && (
              <div className="alert alert-warning">{this.state.error}</div>
            )}
          </form>
        </div>
      </div>
    );
  }
}
