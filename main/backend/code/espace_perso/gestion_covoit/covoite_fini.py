from django.shortcuts import redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib import messages
from ....models import TrajetProposer, ReservationTrajet
from ....forms import TerminerTrajetForm
from ...envoi_email.send_email import envoi_email
from ...securite import reservation_token

def FiniTonCovoiturage(request):
    user = request.user
    trajet_terminer_form = TerminerTrajetForm(request.POST)

    if request.method == "POST" and request.POST.get("form_soumis") == "trajet_terminer_form":

        trajet_terminer_form = TerminerTrajetForm(request.POST)
        trajet_id = request.POST.get("trajet_id")

        if not trajet_id:
            messages.error(request, "Aucun trajet spécifié.")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
        if trajet_terminer_form.is_valid():

                trajet = get_object_or_404(TrajetProposer, id=trajet_id, chauffeur=user)
                # bien mettre trajet.chauffeur et non pas role.chauffeur  ou display comme en html sa ne fonctionne pas, erreur muette
                statut_trajet = trajet_terminer_form.cleaned_data["etat"]
                if statut_trajet == "Terminé":
                    reservations = ReservationTrajet.objects.filter(
                        trajet_reserver=trajet
                    )
                    reservations.update(etat_reservation="Terminé")
                    trajet.etat = statut_trajet
                    trajet.save()
                    messages.success(request, "Vous êtes arrivé à bon port !")

                    if reservations.exists():
                        site_url = f"http://{get_current_site(request).domain}"
                        for res in reservations:
                            passager = res.passager
                            chauffeur = res.trajet_reserver.chauffeur
                            date = res.trajet_reserver.date
                            trajet = res.trajet_reserver
                            token = reservation_token(passager.username)

                            lien_verification = f"{site_url}{reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token})}"
                            subject = "Confirmation de fin de covoiturage"
                            context = {
                                "reservations": reservations,
                                "site_url": site_url,
                                "avis_satisfaction_url": lien_verification,
                                "passager": passager,
                                "chauffeur": chauffeur,
                                "date": date,
                                "trajet": trajet,
                            }
                            envoi_email(request, to=passager.email, subject=subject, template="style_email/covoit_termine.html", context=context)
                        messages.success(request, "Email envoyé avec succès.")
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                else:
                    messages.error(request, "Aucun trajet trouvé.")
                    return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
    else:
        trajet_terminer_form = TerminerTrajetForm()
    return trajet_terminer_form
