# Qu'est ce qu'ECORIDE ?

EcoRide est une plateforme en ligne de covoiturage permettant de simplifier l'échange entre utilisateur , proposer, réserver des covoiturages en toute simplicitée et en cas de soucis notre support est a votre écoute afin de régler tout litige


# ECORIDE – Guide d'installation et de lancement

##  PRÉREQUIS

### Technologies utilisées

**Langages :**
- Python (Back-end)
- HTML (Front-end)
- CSS 3 (Apparence visuelle)
- SQL (Base de données)

**Base de données :**
- PostgreSQL 17 en developpement , 16 en prod

**Framework :**
- Django (framework Python)

**Dépendances supplémentaires :**
- À installer via le terminal :

  pip install -r requirements.txt


##  INSTALLATION

### Sous Windows

1. **Installer les outils nécessaires :**
   - Git : [https://git-scm.com/downloads](https://git-scm.com/downloads)
   - Python 3.13 ou plus récent : [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Node.js (pour Bootstrap) : [https://nodejs.org/fr](https://nodejs.org/fr)

     npm install bootstrap

   - VS Code (éditeur de code) : [https://code.visualstudio.com/](https://code.visualstudio.com/)

2. **Ouvrir VS Code**
   - Cliquer sur les trois petits points en haut à droite → *Terminal* → *Nouveau terminal*

3. **Récupérer le projet :**

   git clone https://github.com/seb-alliot/ECORIDE.git
   cd ECORIDE

4. **Créer et activer l’environnement virtuel :**

   python -m venv venv
   venv\Scripts\activate        # Sous Windows
   source venv/bin/activate       # Sous Mac/Linux

5. **Installer les dépendances :**

   pip install -r requirements.txt

6. **Installer PostgreSQL 17 :**
   [https://www.enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
   ➤ Vérifiez ou modifiez les identifiants de connexion dans `settings.py` > `DATABASES` selon ceux définis lors de l’installation.


##  LANCEMENT DU PROJET

1. **Appliquer les migrations :**

   On utilise l'orm de django via :
      python manage.py makemigrations
      python manage.py migrate

   ou la requete dans le terminal :
      psql -U postgres -d ECORIDE -f main\sql\sql_ecoride.sql


##  CRÉATION D’UN SUPERUTILISATEUR

Dans le terminal :

   python manage.py createsuperuser

   ➤ Suivez les instructions pour créer un compte administrateur.
   ➤ Ensuite, connectez-vous à : `http://127.0.0.1:8000/admin/`

   ou en sql directement via :

   psql -U postgres -d ECORIDE

   INSERT INTO auth_user (
      password,
      last_login,
      is_superuser,
      username,
      first_name,
      last_name,
      email,
      is_staff,
      is_active,
      date_joined
   ) VALUES (
      'bcrypt_sha256$2b$12$GdIcqaELj2HVj6EUdpN5GuZoH88bek3VpvzZFDzSBHuPx5kz0W5A6',
      NOW(),
      TRUE,
      'ITSUKI',
      '',
      '',
      'alliotsebastien@gmail.com',
      TRUE,
      TRUE,
      NOW()
   );

Ce qui donnera user : ITSUKI et mdp : Studietudiant1. en local, sur le serveur y a le même.
le mot de est hasher via bycrypt que j'utilise dans le settings afin que django puisse le reconnaitre par la suite

L'utilisateur Ecoride avec se pseudo est impératif au bon fonctionnement de l'application, l'email  staff.modo.ecoride@gmail.com est recommander mais pas necessaire, le mdp importe peux.



2. **Lancer le serveur local :**

   python manage.py runserver


Projet conçu par **Sebastien Alliot**.
