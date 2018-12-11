import axios from '../lib/axios'
import React from 'react'
import PropTypes from 'prop-types'
import 'react-stepzilla/src/css/main.css'
import qs from 'querystring'
import { hot } from 'react-hot-loader'

import MultiStepForm from './MultiStepForm'
import FormStep from './steps/FormStep'
import ContactStep from './steps/ContactStep'
import LocationStep from './steps/LocationStep'
import ScheduleStep from './steps/ScheduleStep'

import './style.css'

// defined by webpack
const apiEndpoint = API_ENDPOINT // eslint-disable-line no-undef

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
]

class CreateEventForm extends React.Component {
  constructor (props) {
    super(props)
    this.state = { fields: props.initial || {} }
    this.setFields = this.setFields.bind(this)
  }

  async componentDidMount () {
    let subtypes = (await axios.get(apiEndpoint + '/events_subtypes/')).data
    this.setState({ subtypes })
  }

  setFields (fields) {
    this.setState({ fields: Object.assign({}, this.state.fields, fields) })
  }

  render () {
    if (!this.state.subtypes) {
      return null
    }

    let steps = [
      {
        name: 'Quel type ?',
        component: <EventTypeStep setFields={this.setFields} fields={this.state.fields} subtypes={this.state.subtypes} />
      },
      {
        name: 'Qui contacter ?',
        component: <ContactStep setFields={this.setFields} fields={this.state.fields} />
      },
      { name: 'Quand ?', component: <ScheduleStep setFields={this.setFields} fields={this.state.fields} /> },
      { name: 'Où ?', component: <LocationStep setFields={this.setFields} fields={this.state.fields} /> },
      { name: 'Validation et nom', component: <ValidateStep fields={this.state.fields} /> }
    ]

    if (this.props.groups && this.props.groups.length > 0) {
      steps.splice(1, 0, {
        name: 'Qui organise ?',
        component: <OrganizerStep setFields={this.setFields} fields={this.state.fields} groups={this.props.groups} />
      })
    }

    return <MultiStepForm steps={steps} />
  }
}

CreateEventForm.propTypes = {
  'groups': PropTypes.array,
  'initial': PropTypes.object
}

function CheckBoxList ({ children }) {
  return <ul className='nav nav-pills'>
    {children}
  </ul>
}

CheckBoxList.propTypes = {
  children: PropTypes.node
}

function CheckBox ({ label, active, onClick }) {
  return <li className={active ? 'active' : ''}>
    <a href='#' onClick={(e) => {
      e.preventDefault()
      onClick()
    }}> <i className={'fa ' + (active ? 'fa-check-circle' : 'fa-circle-o')} />&nbsp;{label}
    </a>
  </li>
}

CheckBox.propTypes = {
  label: PropTypes.string,
  active: PropTypes.bool,
  onClick: PropTypes.func
}

class EventTypeStep extends FormStep {
  constructor (props) {
    super(props)
    this.rankedSubtypes = props.subtypes.reduce((acc, s) => {
      (acc[s.type] = acc[s.type] || []).push(s)
      return acc
    }, {})
  }

  setSubtype (subtype) {
    this.props.setFields({
      subtype: subtype.label
    })
  }

  isCurrentSubtype (subtype) {
    return subtype.label === this.props.fields.subtype
  }

  isValidated () {
    return !!this.props.fields.subtype
  }

  getRightColumn () {
    if (this.state.isNotCampaign) {
      return (
        <div className='col-sm-6 padbottom'>
          <h3>Je veux créer...</h3>{
            groupTypes.map(type => (
              <div key={type.id}>
                <h4>{type.label}</h4>
                <CheckBoxList>
                  {
                    this.rankedSubtypes[type.id].map(subtype => (
                      <CheckBox key={subtype.description} active={this.isCurrentSubtype(subtype)}
                        label={subtype.description} onClick={() => this.setSubtype(subtype)} />
                    ))
                  }
                </CheckBoxList>
              </div>
            ))
          }
        </div>
      )
    }

    return (
      <div className='col-sm-6 padbottom'>
        <div className='alert alert-danger'>
          Attention&nbsp;! De manière générale, vous ne pouvez pas engager de frais sans la validation du mandataire
          financier de la campagne européenne ou de la France insoumise. Pour vous guider dans la création de votre
          événement, merci d'indiquer les éléments suivants :
        </div>
        <h3>Mon événement...</h3>
        <h5>...est en lien avec la campagne des européennes</h5>
        <p>S'agit-il d'un événement de campagne ?</p>
        <label
          className='radio-inline'> <input type='radio' onClick={() => this.setState({ campaign: true })}
            checked={this.state.campaign} /> Oui </label>
        <label
          className='radio-inline'> <input type='radio' onClick={() => this.setState({ campaign: false })}
            checked={!this.state.campaign} /> Non </label>

        <a className='btn btn-default' href='/formulaires/E19-01/'> Je remplis le formulaire d'accord préalable</a>
        <h5>...un autre événement</h5>
        <p>Ce n'est pas un événement de campagne, ou c'est un événement de campagne qui ne nécessite pas de moyens
          payants. S'il y a un concours gratuit en nature (prêt de salle, de matériel...), vous devez néanmoins
          remplir <a href='https://lafranceinsoumise.fr/app/uploads/2018/11/europennes_dons_en_nature.pdf'> le
            formulaire dédié</a> à l'issue de l'événement.</p>
        <button className='btn btn-default' onClick={() => this.setState({ isNotCampaign: true })}>Je crée directement
          mon événement
        </button>
      </div>
    )
  }

  render () {
    return (
      <div className='row padtopmore'>
        <div className='col-sm-6'>
          <h2>Quel type d'événement voulez-vous créer ?</h2>
          <p>
            Chaque insoumis·e peut créer un événement sur la plateforme dès lors qu’il respecte le cadre et la démarche
            de la France insoumise dans un esprit d’ouverture, de bienveillance et de volonté de se projeter dans
            l’action. </p>
          <p>
            Afin de mieux identifier les événements que vous créez, et de pouvoir mieux les recommander aux autres
            insoumis⋅es, indiquez le type d'événement que vous organisez. </p>
          <p>
            Vous souhaitez inviter un⋅e député⋅e, candidat⋅e, ou animateur⋅ice de livret&nbsp;? {' '} <a
              href='https://lafranceinsoumise.fr/groupes-appui/inviter-des-intervenants/'>Suivez le mode d'emploi.</a>
          </p>
        </div>
        {this.getRightColumn()}
      </div>
    )
  }
}

class OrganizerStep extends FormStep {
  constructor (props) {
    super(props)
    this.setIndividual = this.setIndividual.bind(this)
  }

  setIndividual () {
    this.props.setFields({ organizerGroup: null })
  }

  setGroup (group) {
    this.props.setFields({ organizerGroup: group.id })
  }

  render () {
    const { organizerGroup } = this.props.fields

    return <div className='row padtopmore'>
      <div className='col-sm-6'>
        <h2>Qui organise l'événement ?</h2>
        <p>
          Un événement peut être organisé à titre individuel par une personne. Mais comme vous êtes aussi gestionnaire
          d'un groupe d'action, il est aussi possible d'indiquer que cet événement est organisé par votre groupe. </p>
      </div>
      <div className='col-md-6'>
        <h3>L'événement est organisé...</h3>
        <div>
          <h4>...à titre individuel</h4>
          <CheckBoxList> <CheckBox active={!organizerGroup} label="J'en suis l'organisateur"
            onClick={this.setIndividual} /> </CheckBoxList>
        </div>
        <div>
          <h4>...par un groupe d'action</h4>
          <CheckBoxList>
            {this.props.groups.map((group) => (
              <CheckBox key={group.id} active={group.id === organizerGroup} label={group.name}
                onClick={() => this.setGroup(group)} />
            ))}
          </CheckBoxList>
        </div>
      </div>
    </div>
  }
}

class ValidateStep extends FormStep {
  constructor (props) {
    super(props)
    this.post = this.post.bind(this)
    this.state = { processing: false }
    this.eventNameRef = React.createRef()
  }

  async post (e) {
    e.preventDefault()
    this.setState({ processing: true })

    const { fields } = this.props
    let data = qs.stringify({
      name: this.eventNameRef.current.value,
      contact_email: fields.email,
      contact_name: fields.name || null,
      contact_phone: fields.phone,
      contact_hide_phone: fields.hidePhone,
      start_time: fields.startTime.format('YYYY-MM-DD HH:mm:SS'),
      end_time: fields.endTime.format('YYYY-MM-DD HH:mm:SS'),
      location_name: fields.locationName,
      location_address1: fields.locationAddress1,
      location_address2: fields.locationAddress2 || null,
      location_zip: fields.locationZip,
      location_city: fields.locationCity,
      location_country: fields.locationCountryCode,
      subtype: fields.subtype,
      as_group: fields.organizerGroup
    })

    try {
      let res = await axios.post('form/', data)
      window.location.href = res.data.url
    } catch (e) {
      this.setState({ error: e, processing: false })
    }
  }

  render () {
    const { fields } = this.props
    return (
      <div className='row padtopmore'>
        <div className='col-md-6'>
          <p>Voici les informations que vous avez entrées.</p>
          <ul>
            <li>
              <strong>Type d'événement&nbsp;:</strong> {fields.subtype.label}
            </li>
            <li>
              <strong>Numéro de téléphone&nbsp;:</strong> {fields.phone} ({fields.hidePhone ? 'caché' : 'public'})
            </li>
            {fields.name &&
            <li>
              <strong>Nom du contact pour l'événement&nbsp;:</strong> {fields.name}
            </li>
            }
            <li>
              <strong>Adresse email de contact pour l'événement&nbsp;:</strong> {fields.email}
            </li>
            <li>
              <strong>Horaires&nbsp;:</strong> Du {fields.startTime.format('LLL')} au {fields.endTime.format('LLL')}.
            </li>
            <li>
              <strong>Lieu&nbsp;:</strong><br /> {fields.locationAddress1}<br /> {fields.locationAddress2
                ? <span>{fields.locationAddress2}<br /></span> : ''} {fields.locationZip}, {fields.locationCity}
            </li>
          </ul>
        </div>
        <div className='col-md-6'>
          <p>Pour finir, il vous reste juste à choisir un nom pour votre événement&nbsp;! Choisissez un nom simple et
            descriptif (par exemple : &laquo;&nbsp;Porte à porte près du café de la gare&nbsp;&raquo;).</p>
          <form onSubmit={this.post}>
            <div className='form-group'>
              <input className='form-control' ref={this.eventNameRef} type='text' placeholder="Nom de l'événement"
                required />
            </div>
            <button className='btn btn-primary' type='submit' disabled={this.state.processing}>Créer mon événement
            </button>
          </form>
          {this.state.error && (
            <div className='alert alert-warning'>
              Une erreur s'est produite. Merci de réessayer plus tard. </div>
          )}
        </div>
      </div>
    )
  }
}

export default hot(module)(CreateEventForm)
