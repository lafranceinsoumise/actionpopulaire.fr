import React from 'react';
import Datetime from 'react-datetime';
import moment from 'moment';
import 'moment/locale/fr';

import 'react-datetime/css/react-datetime.css';

import FormStep from './FormStep';


export default class ScheduleStep extends FormStep {
  constructor(props) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.changeStartTime = this.changeStartTime.bind(this);
    this.changeEndTime = this.changeEndTime.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();

    if (typeof this.startTime === 'string' || typeof this.endTime === 'string') {
      this.setState({error: 'Dates invalides'});
      return;
    }

    this.setFields({startTime: this.startTime, endTime: this.endTime});
    this.jumpToStep(this.props.step + 1);
  }

  changeStartTime(value) {
    this.startTime = value;
  }

  changeEndTime(value) {
    this.endTime = value;
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
              <Datetime locale="fr" onChange={this.changeStartTime} />
            </div>
            <div className="form-group">
              <label className="control-label">Fin de l'événement</label>
              <Datetime locale="fr" onChange={this.changeEndTime} />
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
