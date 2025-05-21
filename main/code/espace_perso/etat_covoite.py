from django.shortcuts import get_object_or_404, redirect
from ..envoi_email import Envoi_Email_Annulation

from django.contrib import messages
from django.contrib.auth.models import User
from ...models import TrajetProposer, ReservationTrajet, ChangerStatutTrajet, CreditUser
from ...forms import Demarrer_ou_annulerForm
from django.db import transaction
from django.urls import reverse


def GereTonCovoiteChauffeur(request):
    user = request.user
    demarrer_ou_annuler_form = Demarrer_ou_annulerForm(request.POST)

    trajet_id = request.POST.get("trajet_id")
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()

    if request.method == "POST" and request.POST.get("form_soumis") == "demarrer_ou_annuler_form":

        demarrer_ou_annuler_form = Demarrer_ou_annulerForm(request.POST)
        trajet_id = request.POST.get("trajet_id")
        if demarrer_ou_annuler_form.is_valid():

            # ______PARTIE CHAUFFEUR______

            if request.user == trajet.chauffeur:
                trajet = get_object_or_404(TrajetProposer, id=trajet_id)
                # bien mettre trajet.chauffeur et non pas role.chauffeur  ou display comme en html sa ne fonctionne pas, erreur muette
                statut_trajet = demarrer_ou_annuler_form.cleaned_data["etat"]
                Changer_statut = ChangerStatutTrajet.objects.create(
                trajet=trajet,
                statut=statut_trajet,
                )

                if statut_trajet == "En cours":
                    if TrajetProposer.objects.filter(
                    chauffeur = request.user,
                    etat="En cours"
                    ).exists():
                        messages.info(
                        request,
                        "Un trajet est déjà en cours",
                        )
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                    else:
                        trajet.etat = statut_trajet
                        reservations = ReservationTrajet.objects.filter(
                        trajet_reserver=trajet
                        )
                        reservations.update(etat_reservation="En cours")
                        trajet.save()
                        messages.success(request, "Trajet démarré, bon voyage !")
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                # ______________ANNULATION TRAJET PAR LE CHAUFFEUR_____________

                elif statut_trajet == "Annulé":
                    try:
                        with transaction.atomic():
                            # Récupérer le trajet concerné
                            trajet_reserver = get_object_or_404(
                            TrajetProposer, id=trajet_id
                            )

                            # Vérifier si le trajet a déjà été remboursé
                            if trajet_reserver.trajet_rembourser:
                                messages.error(
                                request,
                                "Le remboursement du trajet a déjà été effectué..",
                            )
                                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                            else:
                                reservations = ReservationTrajet.objects.filter(
                                trajet_reserver=trajet_reserver
                                )
                                total_place_reserver = sum(
                                reservation.places for reservation in reservations
                                )
                                trajet_reserver.places += total_place_reserver
                                trajet_reserver.etat = "Annulé"
                                trajet_reserver.trajet_rembourser = True
                                trajet_reserver.save()

                                # Remboursement des passagers
                                for reservation in reservations:
                                    try:
                                        prix_payer = (
                                        reservation.places * trajet_reserver.prix
                                        )
                                        credit_passager = get_object_or_404(
                                        CreditUser, user=reservation.passager
                                        )
                                        credit_passager.credit += prix_payer
                                        credit_passager.save()

                                        reservation.etat_reservation = "Annulé"
                                        reservation.reservation_rembourser = True
                                        reservation.save()
                                    except Exception as e:
                                        messages.error(
                                        request,
                                        f"Erreur lors du remboursement du passager : {str(e)}",
                                        )
                                        continue

                                    # Redonne la com au chauffeur
                                try:
                                    credit_chauffeur = CreditUser.objects.filter(
                                    user=trajet.chauffeur
                                    ).first()
                                    comission = 2
                                    credit_chauffeur.credit += comission
                                    credit_chauffeur.save()
                                except Exception as e:
                                    messages.error(
                                    request,
                                    f"Erreur lors du retrait des gains du chauffeur : {str(e)}",
                                    )

                                # Retirer la commission de l'admin
                                try:
                                    superuser = User.objects.filter(username='ECORIDE').first()
                                    if superuser:
                                        credit_admin = get_object_or_404(
                                        CreditUser, user=superuser
                                        )
                                        comission_admin = 2
                                        credit_admin.credit -= comission_admin
                                        credit_admin.save()
                                    else:
                                        messages.error(
                                        request,
                                        "L'administrateur n'a pas été trouvé.",
                                        )
                                except Exception as e:
                                    messages.error(
                                    request,
                                    f"Erreur lors du débit de la commission pour la plateforme : {str(e)}",
                                    )

                                # Envoyer l'email d'annulation
                                Envoi_Email_Annulation(request, trajet_id, reservations)
                                messages.success(
                                request,
                                "Covoiturage annulé, les passagers en sont informés par email",
                                )
                                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                    except Exception as e:
                        messages.error(
                        request,
                        f"Erreur lors de l'annulation du trajet : {str(e)}",
                        )
    return demarrer_ou_annuler_form
