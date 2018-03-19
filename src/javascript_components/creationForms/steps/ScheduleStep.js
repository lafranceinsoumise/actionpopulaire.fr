import React from 'react';
import Datetime from 'react-datetime';
import moment from 'moment';
import 'moment/locale/fr';

import 'react-datetime/css/react-datetime.css';

import FormStep from './FormStep';


export default class ScheduleStep extends FormStep {
  constructor(props) {
    super(props);
    this.state.fields = {
      startTime: props.fields.startTime || '',
      endTime: props.fields.endTime || '',
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.changeStartTime = this.changeStartTime.bind(this);
    this.changeEndTime = this.changeEndTime.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();
    if (!this.state.fields.startTime || !this.state.fields.endTime) {
      this.setState({error: 'Tous les champs sont requis.'});
      return;
    }

    if (!this.validateDate(this.state.fields.startTime, this.state.fields.endTime)) {
      return;
    }
    this.setFields({startTime: this.state.fields.startTime, endTime: this.state.fields.endTime});
    this.jumpToStep(this.props.step + 1);
  }

  validateDate(startTime, endTime) {
    if (typeof startTime === 'string' || typeof endTime === 'string') {
      this.setState({error: 'Merci de saisir des dates valides.'});
      return false;
    }

    if (startTime < new Date()) {
      this.setState({error: "L'événement doit se passer dans le futur."});
      return false;
    }

    if (startTime > endTime) {
      this.setState({error: 'La date de début doit être avant la date de fin.'});
      return false;
    }

    this.setState({error: null});
    return true;
  }

  changeStartTime(value) {
    this.setState({
      fields: Object.assign(this.state.fields, {
        startTime: value,
        endTime: null,
      }),
    });
    this.validateDate(value, null);
  }

  changeEndTime(value) {
    this.setState({
      fields: Object.assign(this.state.fields, {
        endTime: value,
      }),
    });
    this.validateDate(this.state.fields.startTime, value);
  }

  render() {
    return (
      <div className="row padtopmore">
        <div className="col-md-6">
          <h4>Calendrier</h4>
          <p>
            Merci de nous indiquer quand aura lieu et combien de temps durera votre événement.
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
              <label className="control-label">Début de l'événement</label>
              <Datetime
                locale="fr"
                onChange={this.changeStartTime}
                isValidDate={d => d.isAfter(Datetime.moment().subtract(1, 'day'))}
                value={this.state.fields.startTime}
              />
            </div>
            <div className="form-group">
              <label className="control-label">Fin de l'événement</label>
              <Datetime
                locale="fr"
                onChange={this.changeEndTime}
                isValidDate={d => d.isAfter((Datetime.moment(this.state.fields.startTime) || Datetime.moment()).clone().subtract(1, 'day'))}
                value={this.state.fields.endTime}
              />
            </div>
            {this.state.error && (
              <div className="alert alert-warning">
                {this.state.error}
              </div>
            )}
            <button className="btn btn-primary" type="submit">Suivant&nbsp;&rarr;</button>
          </form>
        </div>
      </div>
    );
  }
}
