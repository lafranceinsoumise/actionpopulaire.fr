import fontawesome from 'fontawesome';
import Control from 'ol/control/control';

import {element} from './utils';

export default function makeLayerControl(layersConfig) {
  const selectors = layersConfig.map(function (layerConfig) {
    const input = element('input', [], {type: 'checkbox', checked: true});
    const label = element('label', [
      input,
      ['span', [layerConfig.label], {style: {color: layerConfig.color}}]
    ]);

    input.addEventListener('change', function () {
      layerConfig.layer.setVisible(input.checked);
    });

    return label;
  });

  const layerButton = element('button', [fontawesome('bars')]);
  const layerButtonContainer = element(
    'div', [layerButton],
    {className: 'ol-unselectable ol-control layer_selector_button'}
  );

  const layerBox = element('div', selectors, {className: 'layer_selector'});

  layerButton.addEventListener('click', function() {
    layerButton.textContent = layerBox.classList.toggle('visible') ? fontawesome('times') : fontawesome('bars');
  });

  return [
    new Control({element: layerButtonContainer}),
    new Control({element: layerBox})
  ];
}

