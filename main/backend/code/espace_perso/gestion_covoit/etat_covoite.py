from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from ....models import TrajetProposer, ReservationTrajet, ChangerStatutTrajet, CreditUser
from ....forms import Demarrer_ou_annulerForm
from django.db import transaction
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ...utils.zone_admin.recup_commission import get_commission

@login_required
def GereTonCovoiteChauffeur(request):
    user = request.user

    if request.method == "POST" and request.POST.get("form_soumis") == "demarrer_ou_annuler_form":
        demarrer_ou_annuler_form = Demarrer_ou_annulerForm(request.POST)
        trajet_id = request.POST.get("trajet_id")

        if not trajet_id:
            messages.error(request, "Aucun trajet spécifié.")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

        if demarrer_ou_annuler_form.is_valid():
            trajet = get_object_or_404(TrajetProposer, id=trajet_id, chauffeur=user)

            statut_trajet = demarrer_ou_annuler_form.cleaned_data["etat"]
            ChangerStatutTrajet.objects.create(
                trajet=trajet,
                statut=statut_trajet,
            )

            if statut_trajet == "En cours":
                if TrajetProposer.objects.filter(
                    chauffeur=request.user,
                    etat="En cours"
                ).exclude(id=trajet.id).exists():
                    messages.info(request, "Un trajet est déjà en cours")
                    return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                trajet.etat = statut_trajet
                reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet)
                reservations.update(etat_reservation="En cours")
                trajet.save()
                messages.success(request, "Trajet démarré, bon voyage !")
                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

            elif statut_trajet == "Annulé":
                try:
                    with transaction.atomic():
                        if trajet.trajet_rembourser:
                            messages.error(request, "Le remboursement du trajet a déjà été effectué.")
                            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet)
                        total_place_reserver = sum(reservation.places for reservation in reservations)

                        trajet.places += total_place_reserver
                        trajet.etat = "Annulé"
                        trajet.save()
                        messages.success(request, "Trajet annulé, remboursement en cours.")

                        for reservation in reservations:
                            try:
                                prix_payer = reservation.places * trajet.prix
                                credit_passager = get_object_or_404(CreditUser, user=reservation.passager)
                                credit_passager.credit += prix_payer
                                credit_passager.save()

                                reservation.etat_reservation = "Annulé"
                                reservation.reservation_rembourser = True
                                reservation.save()

                                # Email
                                from ...envoi_email.send_email import envoi_email
                                subject = "Annulation de votre trajet"
                                context = {"trajet": trajet, "reservations": reservations}
                                envoi_email(request, to=reservation.passager.email, subject=subject, context=context, template="style_email/annulation_confirmation.html")
                                messages.success(request, "Covoiturage annulé, les passagers en sont informés par email")
                            except Exception as e:
                                messages.error(request, f"Erreur lors du remboursement du passager : {str(e)}")
                                continue
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                except Exception as e:
                    messages.error(request, f"Erreur lors de l'annulation du trajet : {str(e)}")

    return Demarrer_ou_annulerForm()