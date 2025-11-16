let selectMarque = document.getElementById('id_marque');
let selectModele = document.getElementById('id_modele');

if (selectModele) {
    selectModele.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Sélectionnez une marque --';
    selectModele.appendChild(defaultOption);
}

if (selectMarque) {
    selectMarque.addEventListener('change', changeModel);
}

function changeModel(ev) {
    const marque = ev.target.value;

    if (typeof modelsData !== 'undefined' && marque in modelsData) {
        const modeles = modelsData[marque];
        selectModele.innerHTML = '';

        modeles.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            selectModele.appendChild(option);
        });
    }
}
