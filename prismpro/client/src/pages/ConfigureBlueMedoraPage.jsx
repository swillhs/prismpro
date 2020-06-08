import React, { Component } from 'react';

import _ from 'lodash';

// Components
import {
  ElementPlusLabel,
  StackingLayout,
  InputPlusLabel,
  Button,
  Title,
  Alert,
  Modal,
  Loader
} from 'prism-reactjs';

// Utils
import {
  basicFetch
} from '../utils/FetchUtils';

import EntitySearch from '../components/EntitySearch.jsx';

import request_body from './playbook_request_body.json';

class ConfigureBlueMedoraPage extends Component {

  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.createPlaybook = this.createPlaybook.bind(this);
    this.state = {
      buttonEnable: false,
      playbookName: '',
      actionTriggerTypeUuid:'',
      showSuccessBanner: false
    };
  }

  componentDidMount() {
    basicFetch({
      url: '/api/nutanix/v3/action_types/list',
      method: 'POST',
      data: JSON.stringify({
        kind: 'action_type',
        offset: 0,
        length: 40
      })
    }).then(res => {
      this.setState({
        actionTypes: res && res.data && res.data.entities
      });
    });
    const r_body = {
      entity_type: 'trigger_type',
      group_member_attributes: [
        {
          attribute: 'name'
        },
        {
          attribute: 'display_name'
        }
      ],
      filter_criteria: 'name==manual_trigger',
      group_member_count: 20
    };

    const options = {
      method: 'POST',
      url: '/api/nutanix/v3/groups',
      data: JSON.stringify(r_body)
    };
    basicFetch(options).then(res => {
      this.setState({
        actionTriggerTypeUuid: res.data.group_results[0].entity_results[0].entity_id
      });
    });
  }

  modalErrorAlert = (
    <Alert type="error" inline={ true } message="Failed to Initiate Blue Medora" />
  );
  successAlert = (
    <Alert type="success" inline={ false } message="Successfully Initialized Blue Medora" />
  );

  createPlaybook(event) {
    this.setState({ loading : true });
    event.preventDefault();
    try {
      const resources = request_body.spec.resources;
      resources.name = `${this.state.initials} - Increase MSSQL Memory`;
      resources.trigger_list[0].action_trigger_type_reference.uuid =
        this.state.actionTriggerTypeUuid;
      _.forEach(resources.action_list, (action) => {
        const name = action.action_type_reference.name;
        const match = _.find(this.state.actionTypes, type => type.status.resources.name === name);
        action.action_type_reference.uuid = match.metadata.uuid;
        if (name === 'email_action') {
          // Set the email if the action is an email action
          action.input_parameter_values.to_address = this.state.email;
        }
      });
      // eslint-disable-next-line no-console
      console.log('req.body', request_body);
      // Create Playbook Body
      const options = {
        method: 'POST',
        url: '/api/nutanix/v3/action_rules',
        data: JSON.stringify(request_body)
      };
      // Create UDA body
      const options2 = {
        method: 'POST',
        url: '/PrismGateway/services/rest/v2.0/alerts/policies',
        data: JSON.stringify({
          error_on_conflict: false,
          impact_types: ['Performance'],
          title: 'SQL Server Avg Query Latency High',
          description: '',
          filter: 'entity_type==vm',
          auto_resolve: true,
          enabled: true,
          trigger_conditions: [{
            condition_type: 'ANOMALY',
            condition: 'vm.controller_avg_io_latency_usecs',
            severity_level: 'CRITICAL'
          }],
          trigger_wait_period_in_secs: 0
        })
      };
      // Fire and forget the alert policies request
      basicFetch(options2);
      // Wait for alert simulate and basic fetch.
      Promise.all([basicFetch(options), this.simulateAlert()])
        .then(res => {
          this.setState({
            playbookName: '',
            showSuccessBanner: true,
            loading: false
          });
        });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.log('error ', err);
      this.setState({ loading : false });
    }
  }

  simulateAlert() {
    const { entity } = this.state;
    // initiate script
    this.setState({ loading: true });
    return basicFetch({
      url: 'generate_alert/A106472',
      method: 'POST',
      data: JSON.stringify({
        entityId: entity && entity.uuid,
        entityName: entity && entity.name
      })
    });
  }

  handleChange(event) {
    this.setState(
      {
        buttonEnable: true,
        playbookName: event.target.value
      });
  }

  renderModalHeader() {
    return (
      <div className="modal-title-container">
        <Title size="h3">Prism Pro Lab</Title>
      </div>
    );
  }

  getFooter() {
    return (
      <div>
        <Button
          disabled={ this.state.loading || !this.state.initials ||
            !this.state.email || !this.state.entity }
          onClick={ this.createPlaybook }
        >
          Begin
        </Button>
      </div>
    );
  }

  render() {
    return (
      <Modal
        width={ 500 }
        visible={ true }
        footer={ this.getFooter() }
        mask={ false }
        title="Modal"
        maskClosable={ false }
        customModalHeader={ this.renderModalHeader() }
      >
        <Loader loading={ !!this.state.loading }>
          <StackingLayout>
            {this.state.showSuccessBanner ? this.successAlert : null}
            <StackingLayout padding="20px">
              <Title size="h3">Initialize Blue Medora</Title>
              <InputPlusLabel
                value={ this.state.initials }
                onChange={ e =>
                  this.setState({
                    initials: e.target.value
                  })
                }
                label="Enter Your Initials"
                placeholder="Initials" />
              <InputPlusLabel
                value={ this.state.email }
                onChange={ e =>
                  this.setState({
                    email: e.target.value
                  })
                }
                label="Enter Your Email Address"
                placeholder="Email" />
              <ElementPlusLabel
                label="Select your MSSQL VM"
                element={
                  <EntitySearch
                    onEntitiesChange={ selected => this.setState({ entity : selected }) }
                    selectedEntities={ this.state.entity }
                    placeholder="Type to search for you MSSQL VM"
                    entityType="vm"
                    nameAttr="vm_name"
                  />
                }
                helpText="Choose the MSSQL VM you created in the `Deploying MS SQL` lab"
              />
            </StackingLayout>
          </StackingLayout>
        </Loader>
      </Modal>
    );
  }

}

export default ConfigureBlueMedoraPage;
