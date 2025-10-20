const selectMarque = document.getElementById('id_marque')
const selectModele = document.getElementById('id_modele')

if (selectModele) {
    selectModele.innerHTML = ''
    const defaultOption = document.createElement('option')
    defaultOption.value = ''
    defaultOption.textContent = '-- Sélectionnez une marque --'
    selectModele.appendChild(defaultOption)
}

if (selectMarque !== null) {
    selectMarque.addEventListener('change', changeModel)
}

function changeModel(ev) {
    const marque = ev.target.value

    if (marque in modelsData) {
        const modeles = modelsData[marque]

        selectModele.innerHTML = ''

        modeles.forEach((model) => {
            const value = model[0]
            const label = model[1]

            const option = document.createElement('option')
            option.value = value
            option.textContent = label

            selectModele.appendChild(option)
        })
    }
}
