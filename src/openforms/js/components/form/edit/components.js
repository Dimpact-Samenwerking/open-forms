const DECIMAL_PLACES = {
  type: 'number',
  input: true,
  weight: 80,
  key: 'decimalLimit',
  label: 'Decimal Places',
  tooltip: 'The maximum number of decimal places.',
};

const MIN_VALUE = {
  type: 'number',
  label: 'Minimum Value',
  key: 'validate.min',
  input: true,
  placeholder: 'Minimum Value',
  tooltip: 'The minimum value this field must have before the form can be submitted.',
  weight: 150,
};

const MAX_VALUE = {
  type: 'number',
  label: 'Maximum Value',
  key: 'validate.max',
  input: true,
  placeholder: 'Maximum Value',
  tooltip: 'The maximum value this field can have before the form can be submitted.',
  weight: 160,
};

const ALLOW_NEGATIVE = {
  type: 'checkbox',
  input: true,
  label: 'Allow negative values',
  tooltip: 'Allow negative values.',
  key: 'allowNegative',
};

const SUFFIX = {
  type: 'textfield',
  input: true,
  key: 'suffix',
  label: 'A short indicator to discribe the field value.',
};

export {DECIMAL_PLACES, MIN_VALUE, MAX_VALUE, ALLOW_NEGATIVE, SUFFIX};
