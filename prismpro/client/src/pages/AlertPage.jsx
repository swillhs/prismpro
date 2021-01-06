import React, { Component } from 'react';

// Components
import {
  Title,
  Modal,
  StackingLayout,
  ElementPlusLabel,
  Button,
  RadioGroup,
  Radio,
  Loader,
  TextLabel,
  Alert
} from 'prism-reactjs';

import EntitySearch from '../components/EntitySearch.jsx';

// Utils
import {
  basicFetch,
  getErrorMessage
} from '../utils/FetchUtils';

class DefaultPage extends Component {

  state = {
    step: 0,
    radio: 'A120241'
  };

  renderModalHeader() {
    return (
      <div className="modal-title-container">
        <Title size="h3">Easy Ops Lab</Title>
      </div>
    );
  }

  onEntitySearchErr = (e) => {
    if (e && e.message === 'AUTHENTICATION_REQUIRED') {
      this.setState({
        error: 'Failed to authenticate using default password. Please enter your PC Password to continue.'
      });
    } else {
      this.setState({
        error: e
      });
    }
  }

  renderEntityPicker() {
    const { entity } = this.state;
    return (
      <ElementPlusLabel
        label="Select your VM"
        element={
          <EntitySearch
            onEntitiesChange={ selected => this.setState({ entity : selected }) }
            selectedEntities={ entity }
            placeholder="Type to search for your VM"
            entityType="vm"
            nameAttr="vm_name"
            onError={ this.onEntitySearchErr }
          />
        }
        helpText="Choose the VM that you created for this lab"
      />
    );
  }

  renderBody() {
    return (
      <StackingLayout padding="20px">
        <StackingLayout itemSpacing="10px">
          <Title size="h3">Simulate an Alert</Title>
          <div><TextLabel type={ TextLabel.TEXT_LABEL_TYPE.SECONDARY }>
            Select the type of alert to begin.
          </TextLabel></div>
        </StackingLayout>
        <StackingLayout itemSpacing="20px">
          <Title size="h4">Select the type of alert to simulate</Title>
          <RadioGroup
            id="alert_radiogroup"
            defaultValue={ this.state.radio }
            onChange={ e => this.setState({ radio : e.target.value }) }
          >
            <Radio
              value="A120241"
              title="VM Memory Constrained"
            />
            <Radio
              value="A120240"
              title="VM Memory Overprovisioned"
            />
            {/* <Radio
              value="A120245"
              title="VM Bully"
            /> */}
            <Radio
              value="A120094"
              title="Memory Runway is Short"
            />
          </RadioGroup>
        </StackingLayout>
        { this.isClusterAlert() ? null : this.renderEntityPicker() }
      </StackingLayout>
    );
  }

  getButtonText() {
    return 'Simulate Alert';
  }

  completeCurrentStep() {
    this.setState({
      loading: false,
      error: false,
      showAlertSuccess: false
    });

    // simulate alert
    this.simulateAlert(this.state.radio).then(resp => {
      if (resp && resp.stderr) {
        this.setState({
          error: resp.stderr,
          loading: false
        });
      } else {
        this.setState({
          loading: false,
          showAlertSuccess: true
        });
      }
    }).catch(e => {
      // eslint-disable-next-line no-console
      console.log(e);
      this.setState({
        error: e,
        loading: false
      });
    });
  }

  isClusterAlert() {
    return this.state.radio === 'A120094';
  }

  simulateAlert(alert_uid) {
    const { entity } = this.state;
    // initiate script
    this.setState({ loading: true });
    return basicFetch({
      url: `generate_alert/${alert_uid}`,
      method: 'POST',
      data: JSON.stringify({
        entityId: this.isClusterAlert() ? '' : entity && entity.uuid,
        entityName: this.isClusterAlert() ? '' : entity && entity.name
      })
    });
  }

  getFooter() {
    const { entity } = this.state;
    const enabled = entity || this.isClusterAlert();
    return (
      <div>
        <Button disabled={ !enabled } type="primary" onClick={ () => this.completeCurrentStep() }>
          { this.getButtonText() }
        </Button>
      </div>
    );
  }

  renderAlerts() {
    if (this.state.error) {
      return (
        <Alert
          type={ Alert.TYPE.ERROR }
          message={ getErrorMessage(this.state.error) || 'An unknown error occurred.' }
        />
      );
    } else if (this.state.showAlertSuccess) {
      return (
        <Alert
          type={ Alert.TYPE.SUCCESS }
          message="Alert was Successfully Generated."
        />
      );
    }
    return null;
  }

  render() {
    return (
      <Modal
        width={ 500 }
        visible={ true }
        title="Modal"
        footer={ this.getFooter() }
        mask={ false }
        maskClosable={ false }
        customModalHeader={ this.renderModalHeader() }
      >
        <Loader loading={ !!this.state.loading }>
          <StackingLayout>
            { this.renderAlerts() }
            { this.renderBody() }
          </StackingLayout>
        </Loader>
      </Modal>
    );
  }

}

export default DefaultPage;
