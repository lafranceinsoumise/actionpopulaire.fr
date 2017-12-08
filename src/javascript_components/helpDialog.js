import {introJs} from 'intro.js';
import 'intro.js/introjs.css';


module.exports = function () {
  const steps = [];
  const elems = document.getElementsByClassName('help-dialog');

  for (let elem of elems) {
    steps.push(Object.assign({
      element: elem.parentElement,
      intro: elem.innerHTML
    }, elem.dataset));
  }


  const i = introJs();
  i.addSteps(steps);

  i.setOptions({
    nextLabel: 'Suivant &rarr;',
    prevLabel: '&larr; Précédent',
    skipLabel: 'Passer',
    doneLabel: 'Terminé'
  });

  if (steps.length > 0) {
    const buttonContainers = document.getElementsByClassName('help-button');
    for (let buttonContainer of buttonContainers) {
      const link = document.createElement('a');
      link.href = '#';
      link.addEventListener('click', showHints);
      const icon = document.createElement('i');
      icon.className = 'fa fa-question-circle-o';
      link.appendChild(icon);
      buttonContainer.appendChild(link);
    }
  }

  function showHints(e) {
    i.start();
    e.preventDefault();
  }
};
