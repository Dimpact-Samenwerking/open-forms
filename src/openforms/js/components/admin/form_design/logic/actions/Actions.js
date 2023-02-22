import PropTypes from 'prop-types';
import React, {useContext} from 'react';

import {FormContext} from 'components/admin/form_design/Context';
import StepSelection from 'components/admin/form_design/StepSelection';
import DSLEditorNode from 'components/admin/form_design/logic/DSLEditorNode';
import {
  MODIFIABLE_PROPERTIES,
  STRING_TO_TYPE,
  TYPE_TO_STRING,
} from 'components/admin/form_design/logic/constants';
import ComponentSelection from 'components/admin/forms/ComponentSelection';
import JsonWidget from 'components/admin/forms/JsonWidget';
import Select from 'components/admin/forms/Select';

import {ActionError, Action as ActionType} from './types';

const ActionProperty = ({action, errors, onChange}) => {
  const modifiablePropertyChoices = Object.entries(MODIFIABLE_PROPERTIES).map(([key, info]) => [
    key,
    info.label,
  ]);

  const castValueTypeToString = action => {
    const valueType = action.action.property.type;
    const value = action.action.state;
    return TYPE_TO_STRING[valueType](value);
  };

  const castValueStringToType = value => {
    const valueType = action.action.property.type;
    return STRING_TO_TYPE[valueType](value);
  };

  return (
    <>
      <DSLEditorNode errors={errors.component}>
        <ComponentSelection name="component" value={action.component} onChange={onChange} />
      </DSLEditorNode>
      <DSLEditorNode errors={errors.action?.property?.value}>
        <Select
          name="action.property"
          choices={modifiablePropertyChoices}
          translateChoices
          allowBlank
          onChange={e => {
            const propertySelected = e.target.value;
            const fakeEvent = {
              target: {
                name: e.target.name,
                value: {
                  type: MODIFIABLE_PROPERTIES[propertySelected]?.type || '',
                  value: propertySelected,
                },
              },
            };
            onChange(fakeEvent);
          }}
          value={action.action.property.value}
        />
      </DSLEditorNode>
      {MODIFIABLE_PROPERTIES[action.action.property.value] && (
        <DSLEditorNode errors={errors.action?.state}>
          <Select
            name="action.state"
            choices={MODIFIABLE_PROPERTIES[action.action.property.value].options}
            translateChoices
            allowBlank
            onChange={event => {
              onChange({
                target: {
                  name: event.target.name,
                  value: castValueStringToType(event.target.value),
                },
              });
            }}
            value={castValueTypeToString(action)}
          />
        </DSLEditorNode>
      )}
    </>
  );
};

const getVariableChoices = variables => {
  return variables.map(variable => [variable.key, variable.name]);
};

const ActionVariableValue = ({action, errors, onChange}) => {
  const formContext = useContext(FormContext);
  const allVariables = formContext.formVariables;

  return (
    <>
      <DSLEditorNode errors={errors.variable}>
        {/*TODO: This should be a searchable select for when there are a billion variables?*/}
        <Select
          name="variable"
          choices={getVariableChoices(allVariables)}
          allowBlank
          onChange={onChange}
          value={action.variable}
        />
      </DSLEditorNode>
      <DSLEditorNode errors={errors.action?.value}>
        <JsonWidget name="action.value" logic={action.action.value} onChange={onChange} />
      </DSLEditorNode>
    </>
  );
};

const ActionFetchFromService = ({action, errors, onChange}) => {
  return (
    <>
      <DSLEditorNode errors={errors.variable}>
        {/* TODO: ackchyually we want Components ∪ User defined variables */}
        <ComponentSelection name="variable" value={action.variable} onChange={onChange} />
      </DSLEditorNode>
      <DSLEditorNode errors={errors.action?.value}>
        {/* TODO: this element loses state on change of the variable sibling right above*/}
        <input
          name="action.value"
          onChange={onChange}
          value={action.action.value}
          placeholder="ServiceFetchConfiguration id"
          type="number"
        />
      </DSLEditorNode>
    </>
  );
};

const ActionStepNotApplicable = ({action, errors, onChange}) => {
  return (
    <DSLEditorNode errors={errors.formStepUuid}>
      <StepSelection name="formStepUuid" value={action.formStepUuid} onChange={onChange} />
    </DSLEditorNode>
  );
};

const ActionComponent = ({action, errors, onChange}) => {
  let Component;
  switch (action.action.type) {
    case 'property': {
      Component = ActionProperty;
      break;
    }
    case 'variable': {
      Component = ActionVariableValue;
      break;
    }
    case 'fetch-from-service': {
      Component = ActionFetchFromService;
      break;
    }
    case '':
    case 'disable-next': {
      return null;
    }
    case 'step-not-applicable': {
      Component = ActionStepNotApplicable;
      break;
    }
    default: {
      throw new Error(`Unknown action type: ${action.action.type}`);
    }
  }

  return <Component action={action} errors={errors} onChange={onChange} />;
};

ActionComponent.propTypes = {
  action: ActionType.isRequired,
  errors: ActionError,
  onChange: PropTypes.func.isRequired,
};

export {ActionComponent};
