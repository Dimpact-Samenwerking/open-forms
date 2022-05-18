import React from 'react';
import {Tab, TabList, TabPanel, Tabs} from 'react-tabs';
import {FormattedMessage} from 'react-intl';

import Fieldset from '../../forms/Fieldset';
import StaticVariables from './StaticVariables';
import ComponentVariables from './ComponentVariables';
import {VARIABLE_SOURCES} from './constants';
import UserDefinedVariables from './UserDefinedVariables';

const VariablesEditor = ({variables, onAdd, onChange, onDelete}) => {
  return (
    <Fieldset
      title={
        <FormattedMessage
          defaultMessage="Form variables configuration"
          description="Form variables configuration editor fieldset title"
        />
      }
    >
      <Tabs>
        <TabList>
          <Tab>
            <FormattedMessage defaultMessage="Static" description="Static variables tab title" />
          </Tab>
          <Tab>
            <FormattedMessage
              defaultMessage="Component"
              description="Component variables tab title"
            />
          </Tab>
          <Tab>
            <FormattedMessage
              defaultMessage="User defined"
              description="User defined variables tab title"
            />
          </Tab>
        </TabList>

        <TabPanel>
          <StaticVariables
            variables={variables.filter(variable => variable.source === VARIABLE_SOURCES.static)}
          />
        </TabPanel>
        <TabPanel>
          <ComponentVariables
            variables={variables.filter(variable => variable.source === VARIABLE_SOURCES.component)}
          />
        </TabPanel>
        <TabPanel>
          <UserDefinedVariables
            variables={variables.filter(
              variable => variable.source === VARIABLE_SOURCES.userDefined
            )}
            onAdd={onAdd}
            onDelete={onDelete}
            onChange={onChange}
          />
        </TabPanel>
      </Tabs>
    </Fieldset>
  );
};

export default VariablesEditor;
