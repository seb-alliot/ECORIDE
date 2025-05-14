/** creation de bdd voiture foirer, js adapter uniquement a la selection de modele marque */

        const selectMarque = document.getElementById('id_marque')
        const selectModele = document.getElementById('id_modele')

        if(selectMarque !== null) {
            // Lorsque la marque change on exécute la fonction "changeModel"
            selectMarque.addEventListener('change', changeModel)
        }

        function changeModel(ev) {
            const marque = ev.target.value

            if(marque in modelsData) {
                const modeles = modelsData[marque]

                // Supprime toutes les options du <select> des modèles de voiture
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