document.addEventListener('DOMContentLoaded', function() {
    let selectMarque = document.getElementById('id_marque');
    let selectModele = document.getElementById('id_modele');

    // Vérifier que les éléments existent
    if (!selectMarque || !selectModele) {
        console.log('Éléments ajoute_voiture non trouvés');
        return;
    }

    selectModele.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Sélectionnez une marque --';
    selectModele.appendChild(defaultOption);

    selectMarque.addEventListener('change', changeModel);
});

function changeModel(ev) {
    const marque = ev.target.value;
    let selectModele = document.getElementById('id_modele');

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