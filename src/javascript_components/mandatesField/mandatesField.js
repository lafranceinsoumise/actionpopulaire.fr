import React from 'react';
import {hot} from 'react-hot-loader';
import PropTypes from 'prop-types';
import {Modal, Button} from 'react-bootstrap';
import Select from 'react-select';
import Symbol from 'es6-symbol';

import 'react-select/dist/react-select.min.css';

import {mandateGroups, mandateDict} from './divisions';

const mandateOptions = [<option key='' value=''>Choisissez une valeur</option>];

for (let group of mandateGroups) {
  const types = [];
  for (let type of group.mandates) {
    types.push(<option key={type.id} value={type.id}>{type.name}</option>);
  }

  mandateOptions.push(<optgroup key={group.name} label={group.name}>{types}</optgroup>);
}


const emptySelection = {type: '', division: {value: '', label: ''}};


function SelectField({value, divisionDescriptor, onChange}) {
  if ('values' in divisionDescriptor) {
    return <select className="form-control" value={value.value} onChange={e => onChange({value: e.target.value})}>
      <option value=''>Choisissez votre {divisionDescriptor.name.toLowerCase()}</option>
      {divisionDescriptor.values.map(({label, value}) => <option key={value} value={value}>{label}</option>)}
    </select>;
  } else {
    return value.loading ?
      <div>Chargement...</div> :
      <Select.Async value={value} loadOptions={divisionDescriptor.getter.query} onChange={onChange}
                    noResultsText="Pas de résultat" placeholder={divisionDescriptor.name}
                    searchPromptText="Tapez les premiers caractères" loadingPlaceholder="Chargement..."
      />;
  }
}


class MandatesField extends React.Component {
  constructor({hiddenField}) {
    super();

    this.openModal = this.openModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
    this.updateAndClose = this.updateAndClose.bind(this);
    this.addMandate = this.addMandate.bind(this);
    this.prepareSelection = this.prepareSelection.bind(this);

    const fieldValue = hiddenField.value;
    const mandates = fieldValue ?
      JSON.parse(fieldValue) :
      [];

    const currentSelection = mandates
      .filter(m => m.type in mandateDict)
      .map(this.prepareSelection);

    if (currentSelection.length === 0) {
      currentSelection.push(emptySelection);
    }

    this.state = {
      modalIsOpen: false,
      mandates,
      currentSelection
    };

  }

  prepareSelection({type, division}) {
    const divisionType = mandateDict[type].division;
    if ('getter' in divisionType) {
      const symbol = Symbol();
      divisionType.getter.reverse(division).then(
        division => {
          const currentSelection = this.state.currentSelection;
          const i = currentSelection.findIndex(s => s.symbol === symbol && s.type === type);
          if (i !== undefined) {
            this.setState({
              currentSelection: [...currentSelection.slice(0, i), {type, division}, ...currentSelection.slice(i + 1)]
            });
          }
        }
      );
      return {type, division: {loading: true}, symbol};
    }
    return {type, division: {value: division}};
  }

  openModal() {
    this.setState({modalIsOpen: true});
  }

  closeModal() {
    this.setState({modalIsOpen: false});
  }

  updateAndClose() {
    const currentSelection = this.state.currentSelection.map(mandate => (
      {
        type: mandate.type,
        division: mandate.division,
        error: mandate.type !== '' && mandateDict[mandate.type].division !== null && mandate.division.value === ''
      }
    ));

    if (currentSelection.some(m => m.error)) {
      this.setState({currentSelection});
    } else {
      const mandates = currentSelection.map(({type, division}) => ({
        type,
        division: division.value
      })).filter(({type}) => type !== '');
      this.setState({
        mandates,
        currentSelection,
      });
      this.closeModal();
      this.props.hiddenField.value = JSON.stringify(mandates);
    }
  }

  addMandate() {
    const currentSelection = this.state.currentSelection;
    if (currentSelection[currentSelection.length - 1].type !== '') {
      this.setState({currentSelection: [...currentSelection, emptySelection]});
    }
  }

  removeMandate(i) {
    return () => {
      const currentSelection = this.state.currentSelection;
      if (i === currentSelection.length - 1) {
        this.setState({currentSelection: [...currentSelection.slice(0, -1), emptySelection]});
      } else {
        this.setState({currentSelection: [...currentSelection.slice(0, i), ...currentSelection.slice(i + 1)]});
      }
    };
  }

  updateType(i) {
    return e => {
      const currentSelection = this.state.currentSelection.slice();
      currentSelection[i] = Object.assign({}, currentSelection[i], {type: e.target.value});
      this.setState({currentSelection});
    };
  }

  updateDivision(i) {
    return value => {
      const currentSelection = this.state.currentSelection.slice();
      currentSelection[i] = Object.assign({}, currentSelection[i], {division: value});
      this.setState({currentSelection});
    };
  }

  render() {
    const nbMandates = this.state.mandates.length;

    return <div>
      <div>{nbMandates > 0 ? `${nbMandates} mandat${nbMandates > 1 ? 's ' : ' '}` : 'Pas de mandat '}
        <Button onClick={this.openModal}>Modifier</Button></div>
      <Modal bsSize="large" show={this.state.modalIsOpen} onHide={this.closeModal}>
        <Modal.Header closeButton>
          <h4 className="modal-title">Mes mandats électoraux</h4>
        </Modal.Header>
        <Modal.Body>
          <div className="form-horizontal">
            {this.state.currentSelection.map((mandate, i) => (
              <fieldset key={i}>
                <legend>Mandat n°{i + 1}</legend>
                <div className="form-group">
                  <label className="col-sm-2" htmlFor={`type-${i}`}>Type de mandat</label>
                  <div className="col-sm-10">
                    <select className="form-control" id={`type-${i}`} value={mandate.type}
                            onChange={this.updateType(i)}>
                      {mandateOptions}
                    </select>
                  </div>
                </div>
                {
                  mandate.type !== '' && mandateDict[mandate.type].division !== null &&
                  <div className={`form-group${mandate.error ? ' has-error' : ''}`}>
                    <label className="col-sm-2" htmlFor={`division-${i}`}>
                      {mandateDict[mandate.type].division.name}
                    </label>
                    <div className="col-sm-10">
                      <SelectField value={mandate.division} onChange={this.updateDivision(i)}
                                   divisionDescriptor={mandateDict[mandate.type].division}/>
                    </div>
                  </div>
                }
                <Button bsStyle="danger" onClick={this.removeMandate(i)}>
                  Supprimer ce mandat
                </Button>
              </fieldset>
            ))}
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={this.addMandate}>Ajouter un mandat</Button>
          <Button bsStyle="primary" onClick={this.updateAndClose}>Valider les changements</Button>
        </Modal.Footer>
      </Modal>
    </div>;
  }
}

MandatesField.propTypes = {
  hiddenField: PropTypes.object
};

export default hot(module)(MandatesField);
