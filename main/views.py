# coding:utf-8

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from email.header import decode_header

from .forms import (
    Inscription,
    IdentifiantForm,
    MotDePasseForm,
    CustomSetPasswordForm,
    ConfirmEmailForm,
    ReservationTrajetForm,
    AvisForm,
    ContactForm,
    ModerationTrajetForm,
    ModerationAvisPositifForm,
    AfficherTrajetForm,
)
from .models import (
    CreditUser,
    ChoixRole,
    Preference,
    AdresseUser,
    Voiture,
    TrajetProposer,
    ReservationTrajet,
    ActivationToken,
    TokenValidation,
    NoteUser,
)
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetView
)
from .donne_template import (
    InfoTrajet,
    Info_Reservation,
    initialisation_template,
)
from .repeated_code import (
    RechercheTrajet,
    Filtre_trajet
)
from .form_espace_perso import (
    AjoutAdresse,
    ChangeTonRole,
    DonneTesPreferences,
    AjouteTaCaisse,
    ProposeTonCovoiturage,
    FiniTonCovoiturage,
    GereTonCovoiteChauffeur,
    GereTaReservationPassager,
)

from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import CreateView
from django.contrib.auth.models import User
import os, re, uuid, secrets, chardet, random, imaplib, email
from bs4 import BeautifulSoup


# Accueil en definition car fonction simple


def Contact(request):
    user = request.user
    adresse_user = None

    if user.is_authenticated:
        try:
            adresse_user = AdresseUser.objects.get(user=user)
            contact_form = ContactForm(request.POST or None, user=user)
        except AdresseUser.DoesNotExist:
            email = User.objects.get(username=user).email
            contact_form = ContactForm(request.POST or None, initial={"email": email})
    elif user.is_anonymous:
        contact_form = ContactForm(request.POST or None)

    if request.method == "POST":
        if contact_form.is_valid():
            telephone = contact_form.cleaned_data["telephone"]
            pseudo = contact_form.cleaned_data["pseudo"]
            email_user = contact_form.cleaned_data["email"]
            sujet = contact_form.cleaned_data["sujet"]
            message = contact_form.cleaned_data["message"]

            envoi_email_prise_contact(request, telephone, pseudo, email_user, sujet,message )
            return redirect("index")

    context = {
        "adresse_user": adresse_user,
        "contact_form": contact_form,
    }
    context.update(initialisation_template(request))
    return render(
        request,
        "interface_utilisateur/utilisateur/footer/_contact.html",
        context,
    )

def mentions_legales(request):

    context = {}
    context.update(initialisation_template(request))
    return render(
        request,
        "interface_utilisateur/utilisateur/footer/_faq.html",
        context,
    )


def accueil(request):
    user = request.user
    context = {}
    context.update(initialisation_template(request))

    recherche_form, first_resultat, second_resultat = RechercheTrajet(request)
    filtre_form, resultat1, resultat2 = Filtre_trajet(request)

    if request.method == "GET":

        # Formulaire de recherche de trajet
        if recherche_form:
            context["recherche_form"] = recherche_form

        elif filtre_form:
            context["filtre_form"] = filtre_form

    context = {
        # utilisateur
        # recherche
        "first_resultat": first_resultat,
        "second_resultat": second_resultat,

        # filtre
        "resultat1": resultat1,
        "resultat2": resultat2,
        # formulaire de la page
        "filtre_form": filtre_form,
        "recherche_form": recherche_form,
        #envoie des message au template, inutile si balise message dans le template
        "messages": messages.get_messages(request),
    }
    return render(request, "index.html", context)


class UserCreateView(CreateView):

    model = User
    form_class = Inscription
    template_name = "inscription/inscription.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):

        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            ChoixRole.objects.create(role="passager", user=user)
            CreditUser.objects.create(user=user)

            uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
            token = default_token_generator.make_token(user)
            ActivationToken.objects.create(user=user, token=token)

            activation_url = self.request.build_absolute_uri(
                reverse("activation", kwargs={"token": token, "uidb64": uidb64})
            )
            self.ActivationCompte(user, uidb64, activation_url)

            messages.success(self.request, "Votre compte a été créé avec succès.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Une erreur est survenue : {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):

        username = form.data.get("username")
        email = form.cleaned_data.get("email")
        password1 = form.data.get("password1")
        password2 = form.data.get("password2")

        if username and User.objects.filter(username=username).exists():
            messages.error(self.request, "Ce nom d'utilisateur est déjà pris.")

        if email and User.objects.filter(email=email).exists():
            messages.error(self.request, "Cette adresse e-mail est déjà utilisée.")

        if password1 and password2:
            if password1 != password2:
                messages.error(self.request, "Les mots de passe ne correspondent pas.")
            elif not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password1):
                messages.error(
                    self.request,
                    "Le mot de passe doit comporter au moins 8 caractères, avec une majuscule, une minuscule et un chiffre."
                )

        return super().form_invalid(form)

    def ActivationCompte(self, user, uidb64, activation_url):

        subject = "Activation de votre compte EcoRide"
        context = {"user": user, "activation_url": activation_url, "uidb64": uidb64}
        message = render_to_string("style_email/activation_email.html", context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()


def activation(request, uidb64, token):
    try:
        user = urlsafe_base64_decode(uidb64).decode("utf-8")
        activation_token = ActivationToken.objects.get(token=token)
        user = activation_token.user

        if activation_token.is_expired():
            activation_token.delete()
            messages.error(request, "Le lien a expiré.")
            return redirect("inscription")
        user.is_active = True
        credit_user = CreditUser.objects.get(user=user)
        credit_user.credit += 20
        user.save()
        credit_user.save()
        activation_token.delete()
        messages.success(request, "Votre compte a été activé.")
        return redirect("connection1")
    except ActivationToken.DoesNotExist:
        messages.error(request, "Une erreur est survenue.")
        return redirect("inscription")


# ----------------------------reset passaword----------------------------------------------

class CustomPasswordResetView(PasswordResetView):
    form_class = ConfirmEmailForm
    template_name = "réinitialisation/password_reset_form.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            self.user = user
            # Ajouter un message de succès
            messages.success(self.request, "Un email de réinitialisation a été envoyé.")
        except User.DoesNotExist:
            messages.error(self.request, "Aucun utilisateur trouvé avec cet email.")

        return super().form_valid(form)

class CustomResetPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "réinitialisation/password_reset_confirm.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été changé.")
        return super().form_valid(form)

# ------------------------------Connection en 2 étapes------------------------------------------------

# operation 1 : demande d'identifiant
def connection1(request):
    form = IdentifiantForm()

    if request.method == "POST":
        form = IdentifiantForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user = get_user_model().objects.get(username=username)
                if user.is_active:
                    request.session["user_id"] = user.id
                    # gestion du token de session
                    # On le recupere ou renevouvel
                    token, created = TokenValidation.objects.update_or_create(
                        user=user, defaults={"token": get_random_string(32)}
                    )
                    request.session["token"] = token.token

                    email = User.objects.get(username=username).email

                    Deux_F_A(request, email, username)
                    return redirect("connection2")
                else:
                    messages.error(request, "Votre compte n'est pas actif ou inexistant.")
                    return redirect("connection1")
            except get_user_model().DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
                return redirect("connection1")

    context = {
        "form": form,
    }
    context.update(initialisation_template(request))
    return render(request, "login/connection1.html", context)

# operation 2 : demande de mot de passe et code connection 2fa
def connection2(request):
    connected_users = request.session.get("connected_users", [])
    user_id = request.session.get("user_id")
    token = request.session.get("token")
    token_connection_session = request.session.get("token_connection")

    if not token:
        return redirect("connection1")

    if request.method == "POST":
        form = MotDePasseForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]
            token_connection = form.cleaned_data["token_connection"]
            if user_id is None:
                messages.error(request, "L'identifiant n'a pas étè trouvé.")
                return redirect("connection1")
        try:
            user = get_user_model().objects.get(id=user_id)
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user:

                if user_id not in connected_users:
                    connected_users.append(user_id)
                    request.session["connected_users"] = connected_users
                if token_connection_session != token_connection:
                    messages.error(request, "Code de connexion incorrect.")
                    return redirect("connection2")

                TokenValidation.objects.filter(user=user).delete()
                login(request, authenticated_user)
                request.session.pop("user_id", None)
                request.session.pop("token", None)

                messages.info(request, "Vous êtes connecté.")
                return redirect("index")
            else:
                messages.error(request, "Vos identifiants sont érronés.")
                return redirect("connection2")
        except get_user_model().DoesNotExist:
            messages.error(request, "Vos identifiants sont érronés.")
            return redirect("connection1")
    else:
        form = MotDePasseForm()
    context = {
        "form": form,
    }
    context.update(initialisation_template(request))
    return render(request, "login/connection2.html", context)

# --------------------------Deconnection-----------------------------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("/")

# ----------------------Espace Personnel initialisation de données---------------------

# --------------------------Espace Personnel-------------------------------------------
@login_required(login_url="connection1")
def MonCompte(request):
    context = {}

    # Récupération des données utilisateur
    user = request.user

    voiture = Voiture.objects.all().filter(user=user)
    role = ChoixRole.objects.filter(user=user).first()
    preference = Preference.objects.filter(user_preference=user).first()
    note_chauffeur = NoteUser.objects.filter().first()

    adresse_user = AdresseUser.objects.filter(user=user).first()
    if adresse_user is None:
        adresse_user = AdresseUser(user=user, email=user.email)


    # Appel des fontions pour les formulaire
    preference_form = DonneTesPreferences(request)
    role_form = ChangeTonRole(request)
    adresse_form = AjoutAdresse(request)
    voiture_form = AjouteTaCaisse(request)
    trajet_form = ProposeTonCovoiturage(request)
    reservation_form = GereTaReservationPassager(request)
    trajet_terminer_form = FiniTonCovoiturage(request)
    demarrer_ou_annuler_form= GereTonCovoiteChauffeur(request)

    recherche_form, first_resultat, second_resultat = RechercheTrajet(request)
    filtre_form, resultat1, resultat2 = Filtre_trajet(request)

    if request.method == "POST":

        # __________ Formulaire d'ajout d'adresse___________
        if adresse_form:
            context["adresse_form"] = adresse_form
            return redirect("MonCompte")

        # _________Formulaire de choix de rôle___________________
        elif role_form:
            context["role_form"] = role_form
            return redirect("MonCompte")

        # _________Formulaire des preferences chauffeur___________________
        elif preference_form:
            context["preference_form"] = preference_form
            return redirect("MonCompte")

        # __________Formulaire d'ajout de voiture___________
        elif voiture_form:
            context["voiture_form"] = voiture_form
            return redirect("MonCompte")

        # __________Formulaire de proposition de trajet___
        elif trajet_form:
            context["trajet_form"] = trajet_form
            return redirect("MonCompte")

        # Formulaire de trajet terminé
        elif trajet_terminer_form:
            context["trajet_terminer_form"] = trajet_terminer_form
            return redirect("MonCompte")

        # Formulaire de changement de statut de trajet
        elif demarrer_ou_annuler_form:
            context["demarrer_ou_annuler_form"] = demarrer_ou_annuler_form
            return redirect("MonCompte")

        # ______________ANNULATION TRAJET PAR LE PASSAGER____
        elif reservation_form:
            context["reservation_form"] = reservation_form
            return redirect("MonCompte")

    # ______________Recherche de trajet____________________

    if request.method == "GET":

        # Formulaire de recherche de trajet
        if recherche_form:
            context["recherche_form"] = recherche_form

        elif filtre_form:
            context["filtre_form"] = filtre_form

    context.update({
        # utilisateur
        "note_chauffeur": note_chauffeur,
        "role": role,
        "preference": preference,
        "adresse_user": adresse_user,
        "voiture": voiture,

        # recherche
        "first_resultat": first_resultat,
        "second_resultat": second_resultat,

        # filtre
        "resultat1": resultat1,
        "resultat2": resultat2,

        # formulaire
        # __utilisateur__
        "adresse_form": adresse_form,
        "preference_form": preference_form,
        "role_form": role_form,
        "voiture_form": voiture_form,
        # __trajet__
        "demarrer_ou_annuler_form": demarrer_ou_annuler_form,
        "trajet_terminer_form": trajet_terminer_form,
        "trajet_form": trajet_form,
        "filtre_form": filtre_form,
        "recherche_form": recherche_form,
        # __reservation__
        "reservation_form": reservation_form,
        "messages": messages.get_messages(request),
    })

    context.update(InfoTrajet(request))
    context.update(Info_Reservation(request))
    context.update(initialisation_template(request))
    return render(request, "interface_utilisateur/utilisateur/MonCompte.html", context)


# -----------------------------------------------------------------------------------------


def SelectionTrajet(request):
    user = request.user
    # Récupération du trajet
    trajet_id = request.GET.get("trajet_id")
    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    chauffeur = trajet.chauffeur
    try:
        credit_user = (
            CreditUser.objects.get(user=user) if user.is_authenticated else None
        )
        credits = credit_user.credit if credit_user else 0
    except CreditUser.DoesNotExist:
        credits = 0
    try:
        random_commentaire = []
        commentaire_unique = []
        vue_unique_passager = set()
        commentaires = (
            NoteUser.objects.filter(chauffeur=chauffeur)
            .values("commentaire", "passager__username")
            .exclude(commentaire__exact="")
            .exclude(commentaire__isnull=True)
        )
        for commentaire in commentaires:
            if commentaire["passager__username"] not in vue_unique_passager:
                vue_unique_passager.add(commentaire["passager__username"])
                commentaire_unique.append(commentaire)
        random_commentaire = random.sample(
            commentaire_unique, min(len(commentaire_unique), 3)
        )

    except Exception as e:
        random_commentaire = None

        # On creer une liste de commentaire par passager
    commentaire_unique = []
    # On gere les doublons a l'affichage des commentaires pour en avoir un seul par passager
    vue_unique_passager = set()
    # Puis on itères sur les commentaires pour les afficher

    # Récupération des notes du chauffeur
    note_chauffeur = NoteUser.objects.filter(chauffeur=chauffeur).first()

    # Vérification d'une réservation existante pour l'utilisateur
    if not user.is_authenticated:
        reservation = None
    else:
        reservation = ReservationTrajet.objects.filter(
            passager=user, trajet_reserver=trajet
        ).first()

        # Initialisation du formulaire
    reservation_form = ReservationTrajetForm(request.POST or None, instance=reservation)

    # Logique de réservation uniquement pour les utilisateurs authentifiés
    if request.method == "POST" and user.is_authenticated:
        if reservation_form.is_valid():
            places_reservees = reservation_form.cleaned_data["places"]
            if request.POST.get("Reserver") == "oui":

                # Vérification du crédit suffisant
                prix_total = trajet.prix * places_reservees
                if credits < prix_total:
                    messages.error(
                        request, "Vos crédits sont insuffisant pour réserver ce trajet."
                    )
                    return HttpResponseRedirect(f"{reverse('reservation')}?trajet_id={trajet.id}")

                # Vérification du nombre de places disponibles
                elif places_reservees > trajet.places:
                    messages.error(
                        request,
                        "Le nombre de places est insuffisant actuellement pour votre demande.",
                    )
                    return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")
                    #ou return HttpResponseRedirect(f"{reverse('reservation')}?trajet_id={trajet.id}") #

                # Vérification et mise à jour de la réservation
                elif reservation:
                    if reservation.etat_reservation == "Annulé":
                        reservation = ReservationTrajet.objects.create(
                            trajet_reserver=trajet,
                            passager=user,
                            prix_par_passager=prix_total,
                            places=places_reservees,
                        )
                    else:
                        reservation.places += places_reservees
                        reservation.paiement_passager(places_reservees)
                else:
                    reservation = ReservationTrajet.objects.create(
                        trajet_reserver=trajet,
                        passager=user,
                        prix_par_passager=prix_total,
                        places=places_reservees,
                    )
                    credit_user.credit -= prix_total
                    credit_user.save()

                # Mise à jour des places restantes
                trajet.places -= places_reservees
                trajet.save()

                messages.success(request, "La réservation est validée, bonne route !")
                return redirect("MonCompte")
            else:
                messages.error(request, "Vos creédits sont insuffisants pour réserver.")
                return redirect("reservation")

    # Contexte pour le template
    context = {
        "commentaires": random_commentaire,
        "note_chauffeur": note_chauffeur,
        "chauffeur": chauffeur,
        "reservation_trajet": reservation,
        "credits": credits,
        "trajet": trajet,
        "reservation_form": reservation_form,
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(
        request, "interface_utilisateur/utilisateur/reservation/reservation.html", context
    )


@login_required
def AvisSatisfaction(request, trajet_id, token):
    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet).first()
    chauffeur = trajet.chauffeur
    passager = reservation.passager

    # Vérifie si le passager a déjà donné une note ou un commentaire pour ce trajet
    note_existe = NoteUser.objects.filter(
        chauffeur=chauffeur, passager=passager, trajet=trajet
    ).first()

    if request.user != passager:
        messages.error(request, "Vous n'êtes pas sur le bon compte pour répondre à cet email.")
        return redirect("index")

    avis_soumis = None
    avis_form = AvisForm(request.POST)

    if request.method == "POST" and avis_form.is_valid():
        avis_soumis = avis_form.cleaned_data["avis"]
        nouvelle_note = avis_form.cleaned_data["note"]
        nouveau_commentaire = avis_form.cleaned_data["commentaire"]

        if note_existe:
            # Cas où l'utilisateur a déjà donné une note et/ou un commentaire

            if note_existe.avis_donne and avis_soumis != note_existe.avis:
                # Si un avis a déjà été donné, on empêche l'utilisateur de changer son avis
                messages.error(request, "Vous ne pouvez pas modifier votre avis une fois qu'il a été soumis.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))
            if note_existe.note_attribuee and nouvelle_note:
                # Si une note existe déjà, on empêche l'ajout d'une nouvelle
                messages.error(request, "Vous avez déjà donné une note pour ce trajet.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))

            if note_existe.commentaire_attribuee and nouveau_commentaire:
                # Si un commentaire existe déjà, on empêche l'ajout d'un nouveau
                messages.error(request, "Vous avez déjà donné un commentaire pour ce trajet.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))

            # Mise à jour de la note ou du commentaire si possible
            if not note_existe.note_attribuee and nouvelle_note:
                note_existe.note = nouvelle_note
                note_existe.note_attribuee = True
                messages.success(request, "Votre note a bien été prise en compte.")

            if not note_existe.commentaire_attribuee and nouveau_commentaire:
                note_existe.commentaire = nouveau_commentaire
                note_existe.commentaire_attribuee = True
                messages.success(request, "Votre commentaire a bien été pris en compte.")

            note_existe.save()

        else:
            # Création d'une nouvelle note si aucune note existante
            note_existe = NoteUser.objects.create(
                passager=request.user,
                chauffeur=chauffeur,
                trajet=trajet,
                note=nouvelle_note if nouvelle_note else None,
                commentaire=nouveau_commentaire if nouveau_commentaire else None,
                avis_donne=True if avis_soumis else False,
            )
            if nouvelle_note:
                note_existe.note_attribuee = True
            if nouveau_commentaire:
                note_existe.commentaire_attribuee = True
            if avis_soumis:
                note_existe.avis_donne = True
            note_existe.save()

        # Logique pour l'avis "oui" ou "non"
        if avis_soumis:
            commentaire = note_existe.commentaire
            token = None
            if token is None:
                token = uuid.uuid4()

            if avis_soumis == "oui":
                # Crédits au chauffeur
                chauffeur = trajet.chauffeur
                credit_chauffeur = CreditUser.objects.get(user=chauffeur)
                facture_passager = reservation.prix_par_passager
                credit_chauffeur.credit += facture_passager
                credit_chauffeur.save()

                # Envoi email positif
                Envoi_Email_Avis_Trajet_Positif(
                    request, chauffeur, trajet_id, reservation, commentaire, token
                )

            elif avis_soumis == "non":
                # Envoi email négatif
                Envoi_Email_Avis_Trajet_Negatif(
                    request, request.user, trajet_id, reservation, commentaire, token
                )

            return redirect("AvisSatisfaction", trajet_id=trajet_id, token=token)


    context = {
        "note_existe": note_existe,
        "trajet": trajet,
        "chauffeur": chauffeur,
        "reservation": reservation,
        "avis_soumis": avis_soumis,
        "avis_form": avis_form,
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(
        request, "interface_utilisateur/utilisateur/avis_satisfaction.html", context
    )


@user_passes_test(lambda u: u.is_superuser)
def Fait_Ton_Taff_De_Modo(request):

            # Connexion au serveur IMAP
            # Même principe que email dans settings
            mail = imaplib.IMAP4_SSL(
                os.getenv("MAIL_IMAP_SERVER"), int(os.getenv("MAIL_IMAP_PORT"))
            )
            mail.login(os.getenv("MAIL_IMAP_USER"), os.getenv("MAIL_IMAP_PASSWORD"))
            # selectionne la boite de recception cibler a charger
            mail.select("inbox")

            result, data = mail.search(None, "ALL")
            if result != "OK":
                return render(
                    request,
                    "admin/moderateur/moderation_email/moderation_email.html",
                    {"error": "Il n'y a pas d'emails a modérer."},
                )

            mail_ids = data[0].split()
            emails = []

            selected_email = "qu'est ce qui est none?"

            commentaire = "Aucun commentaire trouvé."
            pseudo = "Je s'appel Groot"
            telephone = "Telephone rose bonjour"
            sujet = "qui est née en premier? l'oeuf où la poule?"
            email_user = "celui de ta maman ne fonctionne pas"
            passager = "celui a la place du mort."
            chauffeur = "La mort au volant."
            trajet = "la ou je suis aller"
            date_resa ="le jour ou je meurt"
            reponse_modo = "Aucune réponse trouvée."
            email_type = request.GET.get("email_type", "").strip()

            # Récupération de l'email sélectionné (si existant)
            email_id_selected = request.GET.get("email_id")
            # Si pas d'email on fait en sorte de ne pas générer d'erreur
            for email_id in mail_ids:
                result, data = mail.fetch(email_id, "(RFC822)")
                if result != "OK" or not data or not data[0]:
                    continue

                raw_email = data[0][1]
                if raw_email is None:
                    continue

                message = email.message_from_bytes(raw_email)
                subject, encoding = decode_header(message["Subject"])[0]

                if isinstance(subject, bytes) and encoding:
                    subject = subject.decode(encoding if encoding else "utf-8")
                if subject.lower().startswith("re:"):
                    continue

                # on applique un filtre sur ce que l'on veux sur le template
                sender = message.get("From")
                if not (
                    ("Avis negatif" in subject
                    or "Avis positif" in subject
                    or "Prise de contact" in subject
                    )
                    and ("staff.modo.ecoride@gmail.com" in sender)
                ):
                    continue
                if email_type and email_type not in subject:
                    continue

                body = ""
                # on autopsie l'email recu
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "body/html":
                            gerer_caractere_speciaux = chardet.detect(part.get_payload())
                            if gerer_caractere_speciaux["encoding"]:
                                body = part.get_payload(decode=True).decode(
                                    gerer_caractere_speciaux["encoding"]
                                )
                            else:
                                body = part.get_payload(decode=True).decode()

                            break
                else:
                    body = message.get_payload(decode=True).decode()

                # On extrait le commentaire du passager

                email_data = {
                    "id": email_id.decode(),
                    "subject": subject,
                    "sender": sender,
                    "body": body,
                }
                emails.append(email_data)

                # Si l'email sélectionné correspond à celui-ci, on l'affiche
                if email_id_selected and email_id_selected == email_data["id"]:
                    selected_email = email_data

                    extraire = BeautifulSoup(body, "html.parser")

                    # On extrait le commentaire du passager
                    div_email = extraire.find("div", class_="email_user")
                    if div_email and div_email.p:
                        email_user = (
                            div_email.p.get_text().replace("Email: ", "").strip()
                        )
                    # on fait sauter Commentaire : pour avoir juste le commentaire
                    if email_user.startswith("Email :"):
                        email_user = email_user.replace("Email :", "").strip()

                    # On extrait le commentaire du passager
                    div_commentaire = extraire.find("div", class_="commentaire")
                    if div_commentaire and div_commentaire.p:
                        commentaire = (
                            div_commentaire.p.get_text().replace("Commentaire: ", "").strip()
                        )
                    # on fait sauter Commentaire : pour avoir juste le commentaire
                    if commentaire.startswith("Commentaire :"):
                        commentaire = commentaire.replace("Commentaire :", "").strip()

                    # On extrait le pseudo
                    div_pseudo = extraire.find("div", class_="pseudo")
                    if div_pseudo and div_pseudo.p:
                        pseudo = (
                            div_pseudo.p.get_text().replace("Nom : ", "").strip()
                        )
                    # on fait sauter Pseudo : pour avoir juste le pseudo
                    if pseudo.startswith("Nom :"):
                        pseudo = pseudo.replace("Nom :", "").strip()

                    # On extrait le chauffeur
                    div_passager = extraire.find("div", class_="passager")
                    if div_passager and div_passager.p:
                        passager = (
                            #le seul ou je veux voir passager :
                            div_passager.p.get_text().replace("Passager :", "").strip()
                        )

                    # On extrait le chauffeur
                    div_chauffeur = extraire.find("div", class_="chauffeur")
                    if div_chauffeur and div_chauffeur.p:
                        chauffeur = (
                            div_chauffeur.p.get_text().replace("Chauffeur : ", "").strip()
                        )
                    # on fait sauter chauffeur : pour avoir juste le chauffeur
                    if chauffeur.startswith("Chauffeur:"):
                        chauffeur = chauffeur.replace("Chauffeur :", "").strip()

                    # On extrait le telephone
                    div_telephone = extraire.find("div", class_="telephone")
                    if div_telephone and div_telephone.p:
                        telephone = (
                            div_telephone.p.get_text().replace("telephone :", "").strip()
                        )
                    # on fait sauter telephone : pour avoir juste le telephone
                    if telephone.startswith("telephone :"):
                        telephone = telephone.replace("telephone :", "").strip()

                    # On extrait le sujet
                    div_sujet = extraire.find("div", class_="sujet")
                    if div_sujet and div_sujet.p:
                        sujet = (
                            div_sujet.p.get_text().replace("sujet : ", "").strip()
                        )
                    # on fait sauter sujet : pour avoir juste le sujet
                    if sujet.startswith("sujet:"):
                        sujet = sujet.replace("sujet :", "").strip()

                    # On extrait le trajet
                    div_trajet = extraire.find("div", class_="trajet")
                    if div_trajet and div_trajet.p:
                        trajet = (
                            div_trajet.p.get_text().replace("Trajet : ", "").strip()
                        )
                    # on fait sauter trajet : pour avoir juste le trajet
                    if trajet.startswith("Trajet:"):
                        trajet = trajet.replace("Trajet :", "").strip()


                    # On extrait la date de réservation
                    div_date_reservation = extraire.find("div", class_="date_reservation")
                    if div_date_reservation and div_date_reservation.p:
                        date_resa = (
                            div_date_reservation.p.get_text().replace("Date de réservation : ", "").strip()
                        )
                    # on fait sauter trajet : pour avoir juste le trajet
                    if date_resa.startswith("Date de réservation :"):
                        date_resa = trajet.replace("Date de réservation : :", "").strip()

            moderation_form = ModerationTrajetForm(
                request.POST or None, initial={"commentaire": commentaire}
            )
            contact_form = ContactForm(request.POST or None, initial={"email": email_user,"pseudo":pseudo,"telephone":telephone,"sujet":sujet, "message": commentaire})
            moderation_positive_form = ModerationAvisPositifForm(request.POST or None, initial={"commentaire": commentaire})
            affichage_trajet_form = AfficherTrajetForm(request.POST or None, initial={"chauffeur": chauffeur,"trajet": trajet, "date_reservation": date_resa,"passager":passager})

            if email_type == "Avis negatif":
                if moderation_form.is_valid():
                    choix_moderateur = moderation_form.cleaned_data["etat_paiement"]
                    choix_commentaire = moderation_form.cleaned_data["avis"]
                    try:
                        trajet_id = selected_email["subject"].split(" ")[-1]
                        trajet = TrajetProposer.objects.get(id=trajet_id)
                        reservation = ReservationTrajet.objects.filter(
                            trajet_reserver=trajet
                        ).first()
                        passager = reservation.passager if reservation else None

                        # Récupérer ou créer la note
                        note_chauffeur, created = NoteUser.objects.get_or_create(
                            chauffeur=trajet.chauffeur,
                            passager=passager,
                            trajet=trajet,
                        )
                        note_chauffeur.commentaire = moderation_form.cleaned_data["commentaire"]
                        if choix_commentaire == "oui":
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.etat_paiement = choix_moderateur
                            note_chauffeur.decision_prise = True
                            note_chauffeur.save()
                            messages.info(request, "Le commentaire a bien été enregistré.")
                        elif choix_commentaire == "non":
                            pass

                        if choix_moderateur == "Payer":
                            reservation.etat_paiement = "Payer"
                            credit_chauffeur = CreditUser.objects.get(user=trajet.chauffeur)
                            facture_passager = reservation.prix_par_passager

                            if request.POST.get("Valider") == "oui":
                                credit_chauffeur.credit += facture_passager
                                credit_chauffeur.save()
                                reservation.trajet_payer = True
                                reservation.save()
                                mail.store(email_id, "+FLAGS", "\\Deleted")
                                mail.expunge()
                            messages.success(request, "Le paiement a été accordé.")

                        elif choix_moderateur == "Refuser":
                            reservation.etat_paiement = "Refuser"
                            reservation.trajet_payer = True
                            reservation.save()
                            messages.success(
                                request, "Vous avez bien refusé le paiement au chauffeur."
                            )
                            if request.POST.get("Valider") == "oui":
                                mail.store(email_id, "+FLAGS", "\\Deleted")
                                mail.expunge()
                    except TrajetProposer.DoesNotExist:
                        messages.error(request, "Trajet introuvable.")
                    except ReservationTrajet.DoesNotExist:
                        messages.error(request, "Réservation introuvable.")
                    except CreditUser.DoesNotExist:
                        messages.error(request, "Ce chauffeur n'existe plus.")

            elif email_type == "Avis positif":
                if moderation_positive_form.is_valid():
                    try:
                        trajet_id = selected_email["subject"].split(" ")[-1]
                        trajet = TrajetProposer.objects.get(id=trajet_id)
                        reservation = ReservationTrajet.objects.filter(
                            trajet_reserver=trajet
                        ).first()
                        chauffeur = trajet.chauffeur
                        passager = reservation.passager
                        # Récupérer ou créer l'instance pour appliqué la note
                        note_chauffeur, created = NoteUser.objects.get_or_create(
                            chauffeur=chauffeur,
                            passager=passager,
                            trajet=trajet,
                        )
                        if request.POST.get("action") == "Ajouter":
                            note_chauffeur, created = NoteUser.objects.get_or_create(
                                chauffeur=trajet.chauffeur,
                                passager=passager,
                                trajet=trajet,
                            )
                            note_chauffeur.commentaire = moderation_positive_form.cleaned_data["commentaire"]
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.decision_prise = True
                            note_chauffeur.save()

                            messages.info(request, "Le commentaire a bien été enregistré.")
                            mail.store(email_id, "+FLAGS", "\\Deleted")
                            mail.expunge()
                            messages.success(request, "Le commentaire a bien été enregistré.")
                        elif request.POST.get("action") == "Refuser":
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.decision_prise = True
                            mail.store(email_id, "+FLAGS", "\\Deleted")
                            mail.expunge()
                            messages.success(request, "Votre décision est valider.")

                    except TrajetProposer.DoesNotExist:
                        messages.error(request, "Trajet introuvable.")
                    except CreditUser.DoesNotExist:
                        messages.error(request, "Ce chauffeur n'existe plus.")
                elif request.POST.get("supprimer_email") == "oui":
                    mail.store(email_id, "+FLAGS", "\\Deleted")
                    mail.expunge()
                    messages.success(request, "Email supprimé.")
                else:
                    print(moderation_positive_form.errors)

            elif email_type == "Prise de contact":
                if contact_form.is_valid():

                    reponse_modo = contact_form.cleaned_data["reponse"]
                    Envoi_Reponse_Modo(request, email_user, commentaire , pseudo, reponse_modo)
                    if request.POST.get("repondre") == "oui":
                        mail.store(email_id, "+FLAGS", "\\Deleted")
                        mail.expunge()
                        messages.success(request, "Email supprimé.")


            context = {
                "emails": emails,
                "selected_email": selected_email,
                "messages": messages.get_messages(request),
                "mail_ids": mail_ids,
                "commentaire": commentaire,
                # Formulaire
                "affichage_trajet_form": affichage_trajet_form,
                "moderation_positive_form": moderation_positive_form,
                "contact_form": contact_form,
                "moderation_form": moderation_form,
            }
            context.update(initialisation_template(request))
            return render(
                request, "admin/moderateur/moderation_email/moderation_email.html", context
            )

# ________________Email à factoriser____________________


def envoi_email_prise_contact(request, telephone, pseudo, email_user, sujet,message ):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        contact_url = f"{site_url}{reverse('_contact')}"
        subject = "Prise de contact"
        context = {
            "telephone": telephone,
            "contact_url": contact_url,
            "sujet": sujet,
            "pseudo": pseudo,
            "email_user": email_user,
            "message": message,
            "site_url": site_url,
        }
        message = render_to_string("style_email/contact.html", context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
        )
        email.content_subtype = "html"
        email.send()
        message=request.POST.get("message")
        messages.success(request, "Votre message a bien été envoyé.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail de demande d'information: {str(e)}")
        messages.error(request, f"Erreur lors de l'envoi de l'e-mail de votre retour positif: {str(e)}")


def Envoi_Email_Avis_Trajet_Negatif(
    request, passager, trajet_id, reservations, commentaire, token
):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id, token])}"
        )
        reservation = ReservationTrajet.objects.filter(
            trajet_reserver=trajet_id
        ).first()
        trajet = TrajetProposer.objects.get(id=trajet_id)
        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        chauffeur = trajet.chauffeur
        try:
            telephone = (
                AdresseUser.objects.get(user=chauffeur).telephone
                if AdresseUser.objects.filter(user=chauffeur).exists()
                else None
            )
        except AdresseUser.DoesNotExist:
            telephone = None
        prix_total = reservation.prix_par_passager

        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver

        subject = f"Avis negatif {trajet_id}"

        context = {
            "prix_total": prix_total,
            "telephone": telephone,
            "trajet": trajet,
            "reservations": reservations,
            "site_url": site_url,
            "avis_satisfaction_url": avis_satisfaction_url,
            "passager": passager,
            "chauffeur": chauffeur,
            "date": date,
            "trajet_id": trajet_id,
            "commentaire": commentaire,
        }

        message = render_to_string("style_email/_avis_negatif.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
        )
        email.content_subtype = "html"
        email.send()

        messages.success(
            request, "Votre avis a été envoyer, nous vous remercions pour votre retour."
        )

    except Exception as e:
        print(
            f"Erreur lors de l'envoi de l'e-mail de votre méchant avis pour le chauffeur: {str(e)}"
        )
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de votre retour negatif: {str(e)}",
        )


def Envoi_Email_Avis_Trajet_Positif(
    request, chauffeur, trajet_id, reservations, commentaire, token
):

    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id, token])}"
        )
        reservation = ReservationTrajet.objects.filter(
            trajet_reserver=trajet_id
        ).first()
        trajet = TrajetProposer.objects.get(id=trajet_id)
        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        chauffeur = trajet.chauffeur
        try:
            telephone = (
                AdresseUser.objects.get(user=chauffeur).telephone
                if AdresseUser.objects.filter(user=chauffeur).exists()
                else None
            )
        except AdresseUser.DoesNotExist:
            telephone = None
        prix_total = reservation.prix_par_passager

        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver

        subject = f"Avis positif {trajet_id}"

        context = {
            "prix_total": prix_total,
            "telephone": telephone,
            "trajet": trajet,
            "reservations": reservations,
            "site_url": site_url,
            "avis_satisfaction_url": avis_satisfaction_url,
            "passager": passager,
            "chauffeur": chauffeur,
            "date": date,
            "trajet_id": trajet_id,
            "commentaire": commentaire,
        }

        message = render_to_string("style_email/_avis_positif.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
        )
        email.content_subtype = "html"
        email.send()

        messages.success(
            request, "Votre avis a été envoyer, nous vous remercions pour votre retour."
        )

    except Exception as e:
        print(
            f"Erreur lors de l'envoi de l'e-mail de votre avis sympa pour le chauffeur: {str(e)}"
        )
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de votre retour positif: {str(e)}",
        )


def Envoi_Email_Terminer(request, trajet_id, reservations, token):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id,token])}"
        )

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Confirmation de fin de covoiturage"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": avis_satisfaction_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string("style_email/covoit_termine.html", context)

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="staff.modo.ecoride@gmail.com",
                to=[passager.email],
            )
            email.content_subtype = "html"
            email.send()

    except Exception as e:
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturag : {str(e)}",
        )


def Envoi_Email_Annulation(request, trajet_id, reservations):

    try:
        site_url = f"http://{get_current_site(request).domain}"
        monprofile_url = f"{site_url}{reverse('MonCompte')}"

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Annulation de votre trajet"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "monprofile_url": monprofile_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/annulation_confirmation.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="staff.modo.ecoride@gmail.com",
                to=[passager.email],
            )
            email.content_subtype = "html"
            email.send()

        messages.success(request, "E-mail d'annulation envoyé avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail d'annulation: {str(e)}")
        messages.error(
            request, f"Erreur lors de l'envoi de l'e-mail d'annulation : {str(e)}"
        )


def Deux_F_A(request, email, username):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        connection2_url = f"{site_url}{reverse('connection2')}"

        token_connection = str(secrets.randbelow(1000000)).zfill(6)
        request.session["token_connection"] = token_connection

        subject = "Code de connection"
        context = {
            "username": username,
            "email": email,
            "token_connection": token_connection,
            "site_url": site_url,
            "connection2": connection2_url,
        }

        message = render_to_string(
            "style_email/_2fa.html", context
            )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[email],
        )
        email.content_subtype = "html"
        email.send()

        messages.success(request, "Votre code de connection vous a été envoyer par email.")
        return redirect("connection2")

    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi du code connection: {str(e)}")
        return redirect("connection1")


def Envoi_Reponse_Modo(request, email_user , message , pseudo, reponse_modo):
    try:
        site_url = f"http://{get_current_site(request).domain}"

        subject = "Réponse à votre demande"
        context = {
            "pseudo": pseudo,
            "message": message,
            "reponse_modo": reponse_modo,
            "site_url": site_url,
        }

        message = render_to_string("style_email/_reponse_modo.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[email_user],
        )
        email.content_subtype = "html"
        email.send()
        messages.success(request, "Réponse envoyé.")
    except Exception as e:
        messages.error(request, f"Erreur est survenu : {str(e)}")


# _________________En cour_________________



# _________________A FAIRE_________________


# ------------------------------------A faire avec javascript------------------------------------------------------


# --------retour sur onglet actif dynamique-------
# --------ajout de voiture dynamique-------

#factorisation du code quand j'aurai tout fini , dynamisme fonctionnalité op

# _________________A FINIR_________________

# responsive sur les deux derniere fonctions pour l'admin
