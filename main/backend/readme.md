Fonctionnalités principales ajouté a l'interface admin pour les model TrajetProposer et ReservationTrajet:

Blocage des suppressions, sinon sa interfere avec l'interet de l'historique sur la plateforme

La suppression individuelle et en masse des objets sont interceptée.

Les méthodes delete_model et delete_queryset permettent d’empêcher toute suppression et d’afficher un message d’erreur à l’utilisateur.

Messages personnalisés

Utilisation de django.contrib.messages pour notifier l’administrateur de l’action interdite.

Possibilité de définir différents messages pour suppression individuelle et suppression en masse.

Personnalisation des actions de l’admin

Les actions par défaut comme « Supprimer sélection » peuvent être retirées ou remplacées.

Actions personnalisées (block_delete_selected) peuvent être créées pour appliquer des règles métier spécifiques.

Factorisation avec un mixin

La logique de blocage peut être centralisée dans un BlockDeleteMixin.

Chaque ModelAdmin qui hérite de ce mixin obtient automatiquement le blocage des suppressions et les messages associés.

Permet une maintenance plus simple et une réutilisation sur plusieurs modèles.

Surcharge du save_model sur user lors de la création d'un superuser pour limité leur création a 2, une pour ECORIDE pour le logique metier et le deuxieme pour le proprietaire du site