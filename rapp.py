import streamlit as st
import pandas as pd
import warnings

# Masquer les avertissements de dépréciation dans l'interface
warnings.filterwarnings("ignore", category=UserWarning)

# Le reste de votre code commence ici...
import streamlit as st

# Masquer le logo GitHub, le menu Streamlit et le pied de page par défaut
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import datetime
import sqlite3
import plotly.express as px
from fpdf import FPDF
import sqlite3

# Connexion à votre base de données existante
conn = sqlite3.connect("gestion_it.db")
cur = conn.cursor()

try:
    # Ajout forcé de la colonne 'quantite' si elle n'existe pas
    cur.execute("ALTER TABLE entrees_stock ADD COLUMN quantite INTEGER DEFAULT 1;")
    conn.commit()
    print("Succès : La colonne 'quantite' a été ajoutée à la table entrees_stock.")
except sqlite3.OperationalError as e:
    print("Information : La colonne 'quantite' existe déjà ou autre erreur :", e)
finally:
    conn.close()
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="GESTION D'EQUIPEMENT IT",
    page_icon="💻",
    layout="wide"
)

# --- STYLE CSS (Design épuré, petites cases uniformes, cartes métriques harmonieuses) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stDataFrame {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
    }
    .metric-card-small {
        background-color: #f0f9ff;
        color: #0369a1;
        padding: 10px 12px;
        border-radius: 6px;
        border: 1px solid #bae6fd;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        text-align: center;
        font-weight: 600;
        height: 70px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card-small h3 {
        font-size: 11px;
        margin: 0;
        color: #0284c7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card-small h2 {
        font-size: 18px;
        margin: 2px 0 0 0;
        color: #0f172a;
    }
    .blue-cell-box {
        background-color: #f0f9ff;
        color: #0369a1;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #bae6fd;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 13px;
    }
    .comment-box {
        background-color: #f8fafc;
        border: 1px dashed #0284c7;
        padding: 10px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
        color: #334155;
        font-size: 13px;
    }
    .nav-group-box {
        background-color: #f1f5f9;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }
    .chat-bubble-right {
        background-color: #0284c7;
        color: white;
        padding: 10px 14px;
        border-radius: 16px 16px 0 16px;
        max-width: 65%;
        margin-left: auto;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .chat-bubble-left {
        background-color: #e2e8f0;
        color: #0f172a;
        padding: 10px 14px;
        border-radius: 16px 16px 16px 0;
        max-width: 65%;
        margin-right: auto;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect("gestion_it.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entrees_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_equipement TEXT,
            mois TEXT,
            annee TEXT,
            numero_serie TEXT UNIQUE,
            commentaire TEXT,
            date_entree TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affectations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_equipement TEXT,
            mois_annee_acquisition TEXT,
            numero_serie TEXT UNIQUE,
            lieu TEXT,
            section TEXT,
            departement TEXT,
            date_affectation TEXT,
            commentaire TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reaffectations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_equipement TEXT,
            mois_annee_acquisition TEXT,
            numero_serie TEXT,
            destination TEXT,
            departement TEXT,
            date_reaffectation TEXT,
            commentaire TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS desaffectations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_equipement TEXT,
            section TEXT,
            mois_annee_desaffectation TEXT,
            departement TEXT,
            date_desaffectation TEXT,
            commentaire TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages_outlook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expediteur TEXT,
            message TEXT,
            date_envoi TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cle TEXT UNIQUE,
            valeur TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO config (cle, valeur) VALUES ('password', 'admin')")
    
    conn.commit()
    conn.close()

init_db()

# --- GESTION DE L'AUTHENTIFICATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 20px; margin-bottom: 5px;'>🔐 GESTION D'ÉQUIPEMENT IT</h1>", unsafe_allow_html=True)
    
    # Centrage très compact du logo
    col_img1, col_img2, col_img3 = st.columns([3, 0.8, 3])
    with col_img2:
        try:
            st.image("entreprise.jpg", use_container_width=True)
        except Exception:
            pass  # Ignore si l'image n'est pas trouvée
            
    # Réduction de la largeur du bloc central sans l'encadrement blanc
    col1, col2, col3 = st.columns([1.8, 1, 1.8])
    with col2:
        username = st.text_input("Nom d'utilisateur (admin)")
        password = st.text_input("Mot de passe (admin)", type="password")
        
        conn = sqlite3.connect("gestion_it.db")
        cur = conn.cursor()
        cur.execute("SELECT valeur FROM config WHERE cle='password'")
        pwd_db = cur.fetchone()[0]
        conn.close()
        
        if st.button("Se Connecter", use_container_width=True):
            if username == "admin" and password == pwd_db:
                st.session_state.authentifie = True
                st.session_state.user = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects (Essayez admin / admin)")
                
    st.stop()

# --- STYLE ET BARRE LATÉRALE DE NAVIGATION EN BLEU FONCÉ ---
st.markdown("""
    <style>
    .nav-group-box {
        background-color: #003366;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #004080;
        margin-bottom: 15px;
    }
    .nav-group-box h3, .nav-group-box label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- STYLE ET BARRE LATÉRALE DE NAVIGATION ---
st.markdown("""
    <style>
    /* Remplissage total de la barre latérale avec le dégradé Jaune - Violet - Bleu */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f59e0b 0%, #8b5cf6 50%, #0284c7 100%);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .nav-title {
        color: #ffffff !important;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    /* Style pour la boîte de commentaire élégante en bas de la sidebar */
    .sidebar-footer {
        margin-top: 40px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        font-size: 12px;
        line-height: 1.5;
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h3 class='nav-title'>🗂️ Menu de Navigation</h3>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Aller à", [
    "Tableau de Bord",
    "Entrées Stock IT",
    "Affectations",
    "Réaffectation",
    "Désaffectation",
    "Éditer le formulaire",
    "Rapport Général & Export PDF",
    "Messagerie Outlook & Gmail",
    "Paramètres"
], key="menu_selectbox")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("Déconnexion", use_container_width=True):
    st.session_state.authentifie = False
    st.rerun()

# --- COMMENTAIRE PROFESSIONNEL / PIED DE PAGE DANS LA SIDEBAR ---
st.sidebar.markdown("""
<div class="sidebar-footer">
    <p style="margin-bottom: 4px; font-weight: bold; font-size: 13px;">⚡ Infrastructure & Suivi IT</p>
    <p style="font-style: italic; margin: 0; opacity: 0.95;">"La rigueur et l'organisation sont les clés d'une infrastructure performante et sécurisée."</p>
</div>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def exec_query(query, params=()):
    conn = sqlite3.connect("gestion_it.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_data(query):
    conn = sqlite3.connect("gestion_it.db")
    df = pd.read_sql(query, conn)
    conn.close()
    return df

DEPARTEMENTS_LIST = [
    "IT", "OPERATION", "GATE", "CONTROLLEUR", "RH", "DG", 
    "ITM ENVIRONNEMENT", "MAINTENANCE", "RESPON ACHAT", "ADMINISTRATION", 
    "CONFORMOMITE", "SECURITE", "MAGASSIN", "CAISSE", "PEAGE URBAIN", 
    "CAISSE PARKING", "CUISINE"
]

# --- 1. TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    st.title("📊 Tableau de Bord - GESTION D'ÉQUIPEMENT IT")
    
    st.markdown("---")
    
    # Boîte de bienvenue principale avec un magnifique dégradé (Jaune, Violet, Bleu Ciel) et design ultra-soigné
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f59e0b 0%, #8b5cf6 50%, #0284c7 100%); padding: 22px; border-radius: 12px; border: none; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
        <h4 style="color: #ffffff; margin-top: 0; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Bienvenue sur votre plateforme de gestion centralisée</h4>
        <p style="color: #f8fafc; line-height: 1.6; font-size: 15px; margin-bottom: 0; font-weight: 400;">
            Cette application a été conçue pour optimiser le suivi, la traçabilité et le cycle de vie complet de l'ensemble de votre parc informatique. 
            Elle garantit une visibilité totale sur les mouvements de matériel, de l'acquisition initiale jusqu'à la mise au rebut.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Grille de cartes stylées en bleu avec un fond clair à l'intérieur pour une lisibilité maximale
    col_a, col_b = st.columns(2, gap="medium")
    
    with col_a:
        st.markdown("""
        <div style="background: #f0f7ff; padding: 20px; border-radius: 10px; border: 2px solid #b8daff; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h5 style="color: #004085; margin-top: 0; font-weight: bold;">📥 Gestion des Entrées Stock IT</h5>
            <p style="font-size: 14px; color: #1b1e21; line-height: 1.5; margin-bottom: 0;">
                Centralise l'arrivée de chaque nouvel équipement avec un numéro de série unique.<br>
                <strong>Importance :</strong> Évite les doublons d'inventaire, sécurise la traçabilité dès l'achat et alimente la base de données centrale pour les affectations futures.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f0f7ff; padding: 20px; border-radius: 10px; border: 2px solid #b8daff; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h5 style="color: #004085; margin-top: 0; font-weight: bold;">🔄 Réaffectations Dynamiques</h5>
            <p style="font-size: 14px; color: #1b1e21; line-height: 1.5; margin-bottom: 0;">
                Permet de transférer un matériel d'un service ou d'un département à un autre en toute fluidité.<br>
                <strong>Importance :</strong> Assure un suivi rigoureux des mouvements internes et garde l'historique exact de l'affectation actuelle du matériel.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div style="background: #f0f7ff; padding: 20px; border-radius: 10px; border: 2px solid #b8daff; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h5 style="color: #004085; margin-top: 0; font-weight: bold;">🔗 Suivi des Affectations</h5>
            <p style="font-size: 14px; color: #1b1e21; line-height: 1.5; margin-bottom: 0;">
                Lie directement un équipement en stock à un utilisateur, un bureau, une section ou un département précis.<br>
                <strong>Importance :</strong> Permet de savoir immédiatement qui est responsable de quel matériel en cas de maintenance ou d'audit.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f0f7ff; padding: 20px; border-radius: 10px; border: 2px solid #b8daff; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h5 style="color: #004085; margin-top: 0; font-weight: bold;">❌ Gestion des Désaffectations</h5>
            <p style="font-size: 14px; color: #1b1e21; line-height: 1.5; margin-bottom: 0;">
                Enregistre le retrait définitif des équipements défectueux, obsolètes ou réformés du parc actif.<br>
                <strong>Importance :</strong> Nettoie le parc informatique opérationnel tout en conservant une archive légale des équipements sortants.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # --- PIED DE PAGE INTÉGRÉ AU TABLEAU DE BORD ---
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 15px; color: #666; font-size: 14px;">
        <p style="margin-bottom: 5px; font-weight: bold; color: #0056b3;">Développé par Youri Kalenga</p>
        <p style="font-style: italic; margin: 0;">"La rigueur et l'organisation sont les clés d'une infrastructure informatique performante et sécurisée."</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. ENTRÉES STOCK IT ---
elif menu == "Entrées Stock IT":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #f59e0b 100%); padding: 15px 20px; border-radius: 10px; color: #ffffff; font-weight: bold; font-size: 22px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
        📥 Gestion des Entrées en Stock IT
    </div>
    """, unsafe_allow_html=True)
    
    # En-tête explicatif avec le dégradé complet
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #f59e0b 100%); padding: 18px; border-radius: 10px; color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
        <strong>Procédure de Réception & Entrée en Stock :</strong> 
        Enregistrez ici l'arrivée de nouveaux équipements informatiques. Assurez-vous de renseigner les informations d'origine, l'état physique, l'emplacement de stockage ainsi que les accessoires fournis pour garantir une traçabilité complète.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_entree_stock", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Identification & Matériel**")
            nom_equipement = st.text_input("Nom / Type d'équipement", placeholder="Ex: PC Portable Dell, Switch Cisco")
            
            if nom_equipement.strip() != "":
                quantite = st.number_input("Quantité", min_value=1, value=1, step=1, key="qte_dynamique")
            else:
                quantite = 1
                
            numero_serie = st.text_input("Numéro de Série (S/N) *", placeholder="Ex: SN123456789")
            adresse_mac = st.text_input("Adresse MAC (Si applicable)", placeholder="Ex: AA:BB:CC:DD:EE:FF")
            
            st.markdown("**2. Origine & Achat**")
            fournisseur = st.text_input("Fournisseur / Vendeur", placeholder="Ex: TMB, Fournisseur Local")
            ref_bl = st.text_input("N° de Bon de Livraison / Facture (BL)", placeholder="Ex: BL-2026-08")
            
            mois = st.selectbox("Mois d'acquisition", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
            annee = st.text_input("Année d'acquisition", value=str(datetime.date.today().year))

        with col2:
            st.markdown("**3. Logistique, Stockage & État**")
            etat_reception = st.selectbox("État à la réception", ["Neuf (New)", "Reconditionné (Refurbished)", "Retour en stock (Désaffectation)"])
            emplacement = st.text_input("Emplacement de stockage", placeholder="Ex: Armoire A, Étagère 2")
            responsable = st.text_input("Technicien Réceptionnaire", placeholder="Ex: Emmanuel")
            
            st.markdown("**4. Accessoires & Conformité (*)**")
            col_acc1, col_acc2 = st.columns(2)
            with col_acc1:
                acc_chargeur = st.checkbox("* Chargeur / Alimentation")
                acc_cable = st.checkbox("* Câbles réseau / Connexion")
            with col_acc2:
                acc_emballage = st.checkbox("* Emballage intact / Conforme")
                acc_doc = st.checkbox("* Manuels / Documentation")
            
            commentaire_input = st.text_area("Commentaire d'entrée", placeholder="Détails supplémentaires sur la réception...")

        date_entree = datetime.date.today().strftime("%Y-%m-%d")
        
        # Construction d'un commentaire enrichi intégrant tous les nouveaux détails
        commentaire_final = (
            f"Reçu le {date_entree} | Fournisseur: {fournisseur if fournisseur else 'N/A'} (BL: {ref_bl if ref_bl else 'N/A'}) | "
            f"État: {etat_reception} | Emplacement: {emplacement if emplacement else 'N/A'} | "
            f"Tech: {responsable if responsable else 'N/A'} | MAC: {adresse_mac if adresse_mac else 'N/A'} | "
            f"Accessoires [Chargeur: {'Oui' if acc_chargeur else 'Non'}, Câble: {'Oui' if acc_cable else 'Non'}, Emballage: {'Oui' if acc_emballage else 'Non'}] | "
            f"Note: {commentaire_input}"
        )
        
        st.markdown("---")
        submit_entree = st.form_submit_button("Enregistrer l'Entrée en Stock", use_container_width=True)
        
        if submit_entree:
            if nom_equipement and numero_serie:
                try:
                    exec_query(
                        "INSERT INTO entrees_stock (nom_equipement, quantite, mois, annee, numero_serie, commentaire, date_entree) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (nom_equipement, quantite, mois, annee, numero_serie, commentaire_final, date_entree)
                    )
                    st.success("Entrée de stock enregistrée avec succès !")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Erreur : Ce numéro de série existe déjà dans la base de données.")
            else:
                st.warning("Veuillez remplir au moins le nom de l'équipement et le numéro de série.")
            
    # Titre du tableau avec le dégradé complet
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #f59e0b 100%); padding: 12px 18px; border-radius: 8px; color: #ffffff; font-weight: bold; font-size: 16px; margin-top: 25px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
        📋 Tableau des Entrées de Stock
    </div>
    """, unsafe_allow_html=True)

    df_e = get_data("SELECT * FROM entrees_stock")
    if not df_e.empty:
        st.dataframe(df_e, width='stretch')
    else:
        st.info("Aucune entrée en stock pour le moment.")

    # --- SECTION POUR VIDER LE TABLEAU ---
    st.markdown("---")
    with st.expander("⚠️ Zone de danger : Vider le tableau"):
        confirmation_vider = st.checkbox("Je confirme vouloir supprimer toutes les données de cette table")
        if st.button("🗑️ Vider tout le tableau des entrées", use_container_width=True):
            if confirmation_vider:
                exec_query("DELETE FROM entrees_stock")
                st.success("Le tableau a été entièrement vidé avec succès !")
                st.rerun()
            else:
                st.warning("Veuillez cocher la case de confirmation pour vider le tableau.")
# --- 3. AFFECTATIONS ---
elif menu == "Affectations":
    st.title("🔗 Nouvelle Affectation d'Équipement")
    
    # Commentaire intelligent au-dessus du formulaire
    st.markdown("""
        <div style="padding: 12px 15px; border-radius: 8px; background-color: #f0f4f8; border-left: 5px solid #0066cc; margin-bottom: 20px;">
            <p style="margin: 0; color: #1e293b; font-size: 14px;">
                <b>ℹ️ Guide :</b> Recherchez et sélectionnez l'équipement enregistré dans les stocks. Renseignez ensuite les informations du bénéficiaire, les responsables, l'état initial ainsi que le lieu, la section et le département d'affectation avant de valider.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    df_entrees = get_data("SELECT DISTINCT nom_equipement, mois, annee, numero_serie, commentaire FROM entrees_stock")
    
    if df_entrees.empty:
        st.warning("Veuillez d'abord enregistrer des équipements dans les Entrées Stock IT.")
    else:
        recherche_nom = st.text_input("Rechercher / Saisir le nom de l'équipement")
        df_filtered = df_entrees[df_entrees['nom_equipement'].str.lower().str.startswith(recherche_nom.lower())] if recherche_nom else df_entrees
            
        if not df_filtered.empty:
            choix_nom = st.selectbox("Nom de l'équipement reconnu", df_filtered['nom_equipement'].tolist())
            equip_info = df_filtered[df_filtered['nom_equipement'] == choix_nom].iloc[0]
            
            with st.form("form_affectation"):
                
                # --- BLOC 1 : INFORMATIONS SUR LE BÉNÉFICIAIRE ---
                st.markdown("#### 👤 1. Informations sur le Bénéficiaire et l'Affectation")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    nom_beneficiaire = st.text_input("Nom du bénéficiaire", placeholder="Ex: Jean Dupont")
                    fonction_poste = st.text_input("Fonction / Poste", placeholder="Ex: Comptable, Ingénieur, Développeur")
                with col_b2:
                    type_affectation = st.selectbox("Type d'affectation", [
                        "Dotation définitive",
                        "Prêt temporaire",
                        "Matériel mis en commun (Pool)"
                    ])
                
                st.markdown("---")
                
                # --- BLOC 2 : ÉQUIPEMENT ET LOCALISATION (Votre code d'origine) ---
                st.markdown("#### 💻 2. Caractéristiques et Localisation")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Nom de l'équipement", value=choix_nom, disabled=True)
                    mois_annee_acq = st.text_input("Mois & Année d'acquisition", value=f"{equip_info['mois']} {equip_info['annee']}")
                    serie = st.text_input("Numéro de Série", value=equip_info['numero_serie'])
                with col2:
                    lieu = st.text_input("Lieu", placeholder="Ex: Bureau 204, Site Principal")
                    section = st.text_input("Section", placeholder="Ex: Infrastructure / Support")
                    departement = st.selectbox("Département", DEPARTEMENTS_LIST)
                
                st.markdown("---")
                
                # --- BLOC 3 : ACTEURS ET RESPONSABLES (Traçabilité) ---
                st.markdown("#### ✍️ 3. Acteurs et Responsables (Traçabilité)")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    technicien_installateur = st.text_input("Technicien / Installateur", placeholder="Nom du technicien déployeur")
                with col_act2:
                    validateur_superviseur = st.text_input("Validateur / Superviseur", placeholder="Nom du Manager / Chef de service")

                st.markdown("---")

                # --- BLOC 4 : ÉTAT INITIAL ET ACCESSOIRES ---
                st.markdown("#### 🎒 4. État initial et Accessoires fournis")
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    peripheriques_associes = st.multiselect("Périphériques & Accessoires associés", [
                        # Stockage & Alimentation
                        "Chargeur spécifique", "Batterie externe (Powerbank)", "Station d'accueil / Dock Station", "Multiprise parafoudre", "Rallonge électrique", "Onduleur personnel", "Disque dur externe", "Clé USB", "Carte mémoire SD/MicroSD", "Boîtier disque dur externe",
                        # Saisie & Navigation
                        "Souris filaire", "Souris sans fil", "Clavier filaire", "Clavier sans fil", "Kit Clavier & Souris", "Tapis de souris ergonomique", "Pavé numérique externe", "Stylet / Digital Pen", "Tablette graphique", "Présentateur laser / Clicker",
                        # Affichage & Vidéo
                        "Écran externe 21\"", "Écran externe 24\"", "Écran externe 27\"", "Support double écran", "Adaptateur HDMI vers VGA", "Adaptateur DisplayPort vers HDMI", "Câble HDMI", "Câble DisplayPort", "Câble VGA", "Câble DVI", "Câble USB-C vers HDMI", "Adaptateur Multiport USB-C", "Webcam HD", "Webcam 4K", "Répétiteur de signal / Dongle Miracast",
                        # Audio & Communication
                        "Casque audio avec micro", "Écouteurs filaires", "Écouteurs Bluetooth", "Microphone de bureau", "Enceinte Bluetooth portable", "Barre de son", "Téléphone IP / VoIP", "Casque téléphonique Call Center",
                        # Réseau & Connectivité
                        "Câble réseau RJ45 Cat5e", "Câble réseau RJ45 Cat6", "Câble réseau RJ45 Cat6a", "Câble RJ45 blindé (S/FTP)", "Câble fibre optique Patchcord", "Adaptateur USB vers Ethernet RJ45", "Clé Wi-Fi USB", "Routeur Wi-Fi 4G/5G portable", "Switch réseau non manageable 5 ports", "Switch réseau non manageable 8 ports", "Injecteur PoE", "Splitter PoE",
                        # Sécurité & Protection
                        "Sacoche pour ordinateur portable", "Sac à dos technique IT", "Housse de protection souple", "Antivol physique pour ordinateur (Kensington)", "Filtre de confidentialité pour écran", "Kit de nettoyage écran et matériel", "Gants antistatiques", "Badge d'accès RFID / NFC",
                        # Impression, Scan & Lecture
                        "Imprimante thermique de reçus", "Douchette / Scanner code-barres USB", "Lecteur de badge magnétique", "Lecteur de carte à puce / Smart Card",
                        # Outillage & Maintenance IT de terrain
                        "Pince à sertir RJ45", "Testeur de câble réseau RJ45", "Tournevis de precision IT (Kit)", "Multimètre numérique", "Bombe d'air sec dépoussiérant", "Lingettes nettoyantes professionnelles", "Colliers de serrage (Rilsans)", "Goulotte passe-câbles", "Étiqueteuse portable", "Ruban pour étiqueteuse",
                        # Divers
                        "Support PC portable inclinable", "Lampe de bureau USB", "Porte-badge professionnel", "Cadenas de sécurité"
                    ], default=["Chargeur spécifique", "Souris sans fil", "Sacoche pour ordinateur portable"])
                with col_acc2:
                    etat_cosmetique = st.selectbox("État cosmétique / technique à la livraison", [
                        "Neuf (Emballé)",
                        "Excellent état",
                        "Bon état (Traces d'usure légères)",
                        "Reconditionné"
                    ])

                st.markdown("---")
                    
                date_affectation = datetime.date.today().strftime("%Y-%m-%d")
                
                # Formatage enrichi du commentaire final
                accessoires_str = ", ".join(peripheriques_associes) if peripheriques_associes else "Aucun"
                commentaire_final = st.text_area(
                    "Commentaire en dessous", 
                    value=f"Bénéficiaire: {nom_beneficiaire or 'N/A'} ({fonction_poste or 'N/A'}) | Type: {type_affectation} | Tech: {technicien_installateur or 'N/A'} | Validateur: {validateur_superviseur or 'N/A'} | État: {etat_cosmetique} | Accessoires: {accessoires_str} | Entrée d'origine : {equip_info['commentaire']}"
                )
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    submit_aff = st.form_submit_button("Valider l'Affectation", use_container_width=True)
                with col_a2:
                    clear_aff = st.form_submit_button("Vider", use_container_width=True)
                    
                if submit_aff:
                    try:
                        # 1. Insertion dans la table principale des affectations
                        exec_query(
                            "INSERT INTO affectations (nom_equipement, mois_annee_acquisition, numero_serie, lieu, section, departement, date_affectation, commentaire) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (choix_nom, mois_annee_acq, serie, lieu, section, departement, date_affectation, commentaire_final)
                        )
                        
                        # 2. Création et insertion dans la table de preuves de pertes (invisible dans les rapports généraux)
                        exec_query("""
                            CREATE TABLE IF NOT EXISTS preuves_pertes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                numero_serie TEXT,
                                nom_equipement TEXT,
                                nom_beneficiaire TEXT,
                                fonction_poste TEXT,
                                type_affectation TEXT,
                                technicien_installateur TEXT,
                                validateur_superviseur TEXT,
                                etat_cosmetique TEXT,
                                accessoires_fournis TEXT,
                                date_affectation TEXT
                            )
                        """)
                        exec_query("""
                            INSERT INTO preuves_pertes (numero_serie, nom_equipement, nom_beneficiaire, fonction_poste, type_affectation, technicien_installateur, validateur_superviseur, etat_cosmetique, accessoires_fournis, date_affectation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (serie, choix_nom, nom_beneficiaire, fonction_poste, type_affectation, technicien_installateur, validateur_superviseur, etat_cosmetique, accessoires_str, date_affectation))

                        st.success("Affectation enregistrée et preuve de traçabilité archivée avec succès !")
                        st.rerun() # Recharger pour mettre à jour l'affichage
                    except sqlite3.IntegrityError:
                        st.error("Erreur : Ce numéro de série est déjà affecté.")
                if clear_aff:
                    st.rerun()

    st.markdown('<div class="blue-cell-box">Tableau des Affectations</div>', unsafe_allow_html=True)
    df_a = get_data("SELECT * FROM affectations")
    
    if not df_a.empty:
        st.dataframe(df_a, width='stretch')
        
        # Bouton pour vider le tableau
        if st.button("🗑️ Vider le tableau des affectations", type="primary"):
            if "confirm_aff_delete" not in st.session_state:
                st.session_state.confirm_aff_delete = True
            
        if st.session_state.get("confirm_aff_delete", False):
            st.warning("⚠️ Êtes-vous sûr de vouloir supprimer TOUTES les données d'affectation ?")
            col_a1, col_a2 = st.columns(2)
            if col_a1.button("Oui, supprimer tout"):
                exec_query("DELETE FROM affectations")
                st.session_state.confirm_aff_delete = False
                st.rerun()
            if col_a2.button("Annuler"):
                st.session_state.confirm_aff_delete = False
                st.rerun()
    else:
        st.info("Le tableau des affectations est vide.")

    # --- SECTION SECRÈTE DE GESTION DES PREUVES EN CAS DE PERTE ---
    with st.expander("🛡️ Registre de Preuves de Traçabilité (Réservé Sécurité / Perte)"):
        st.caption("Cette table contient l'historique détaillé des acteurs et des accessoires fournis pour chaque numéro de série en cas de litige ou de perte (exclu des rapports standards).")
        
        try:
            df_preuves = get_data("SELECT * FROM preuves_pertes")
        except:
            df_preuves = pd.DataFrame()

    if not df_preuves.empty:
        st.dataframe(df_preuves, width='stretch')
    
    # Bouton pour vider le tableau des preuves de pertes
    if st.button("🗑️ Vider le registre des preuves de pertes", type="primary", key="btn_clear_preuves"):
        if "confirm_preuves_delete" not in st.session_state:
            st.session_state.confirm_preuves_delete = True
                
            if st.session_state.get("confirm_preuves_delete", False):
                st.warning("⚠️ Êtes-vous sûr de vouloir supprimer TOUTES les preuves de traçabilité ?")
                col_p1, col_p2 = st.columns(2)
                if col_p1.button("Oui, supprimer tout", key="yes_del_preuves"):
                    exec_query("DELETE FROM preuves_pertes")
                    st.session_state.confirm_preuves_delete = False
                    st.rerun()
                if col_p2.button("Annuler", key="cancel_del_preuves"):
                    st.session_state.confirm_preuves_delete = False
                    st.rerun()
        else:
            st.info("Aucune preuve enregistrée pour le moment.")
# --- 4. RÉAFFECTATION ---
elif menu == "Réaffectation":
    st.title("🔄 Réaffectation d'Équipement")
    
    # En-tête explicatif soigné et professionnel
    st.markdown("""
    > **Procédure de Réaffectation Sécurisée** : 
    > Cette section permet de redéployer un équipement informatique au sein d'un nouveau département ou site tout en garantissant sa traçabilité, sa conformité logicielle et son bon état technique. Veuillez valider les contrôles requis avant la validation finale.
    """)
    
    df_affect = get_data("SELECT * FROM affectations")
    
    if df_affect.empty:
        st.warning("Aucune affectation active reconnue.")
    else:
        serie_sel = st.selectbox("Sélectionner par numéro de série", df_affect['numero_serie'].tolist())
        curr_info = df_affect[df_affect['numero_serie'] == serie_sel].iloc[0]
        
        # Affichage rapide des informations actuelles de l'équipement dans une boîte stylée
        st.info(f"📍 **Affectation actuelle :** Lieu : `{curr_info.get('lieu', 'N/A')}` | Département : `{curr_info.get('departement', 'N/A')}`")
        
        with st.form("form_reaffect"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                destination = st.text_input("Destination (Nouveau Bureau / Site)")
                nouveau_beneficiaire = st.text_input("Nouveau Bénéficiaire", placeholder="Ex: Jean Dupont")
            with col_d2:
                nouveau_dept = st.selectbox("Nouveau Département", DEPARTEMENTS_LIST)
                
            # --- SECTION INTERVENANTS & CATÉGORIES DE PERSONNES ---
            st.markdown("---")
            st.markdown("### 👥 Acteurs & Intervenants de la Réaffectation")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                nom_superviseur = st.text_input("Superviseur / Validateur", placeholder="Ex: Amed")
                nom_technicien = st.text_input("Technicien en charge", placeholder="Ex: Emmanuel")
            with col_p2:
                chef_departement = st.text_input("Chef de Département", placeholder="Ex: Responsable DSI")
                responsable_securite = st.text_input("Référent Sécurité / IT", placeholder="Ex: Securité Admin")
            with col_p3:
                valideur_finance = st.text_input("Validation Finance / Actifs", placeholder="Ex: Comptabilité")
                ressource_rh = st.text_input("Contact RH / Gestion", placeholder="Ex: Ressources Humaines")
            # -------------------------------------------------------------
            
            # --- CHECKLIST DE PRÉPARATION & VALIDATION TECHNIQUE ---
            st.markdown("---")
            st.markdown("### 📋 Checklist de Préparation & Validation Technique")
            
            # Organisation en 2 colonnes compactes avec des libellés clairs
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                st.markdown("**1. Diagnostic & Matériel**")
                chk_diag = st.checkbox("* Contrôle technique (RAM, disque, état)")
                chk_clean_phys = st.checkbox("* Nettoyage physique & dépoussiérage")
                chk_upgrade = st.checkbox("* Mise à niveau (SSD / RAM si besoin)")
                
                st.markdown("**2. Sécurité & Données**")
                chk_wipe = st.checkbox("* Formatage & réinstallation propre (OS)")
                chk_data_del = st.checkbox("* Purge des anciennes données")
                chk_domain = st.checkbox("* Intégration Domaine / MDM / GPO")
            
            with col_c2:
                st.markdown("**3. Logistique & Suivi**")
                chk_cmdb = st.checkbox("* Mise à jour Inventaire / CMDB")
                chk_licences = st.checkbox("* Réattribution des licences logicielles")
                
                st.markdown("**4. Recette & Validation**")
                chk_test = st.checkbox("* Tests fonctionnels (Réseau / Périphériques)")
                chk_pv = st.checkbox("* PV de remise signé par le bénéficiaire")
            
            date_reaff = datetime.date.today().strftime("%Y-%m-%d")
            
            # Construction dynamique du commentaire enrichi avec les différents acteurs
            default_comment = (
                f"Réaffecté le {date_reaff} vers {destination} ({nouveau_dept}) - Bénéficiaire : {nouveau_beneficiaire}. "
                f"Équipe [Tech: {nom_technicien if nom_technicien else 'N/A'}, Sup: {nom_superviseur if nom_superviseur else 'N/A'}, Chef Dpt: {chef_departement if chef_departement else 'N/A'}]. "
                f"Contrôles [Diag: {'OK' if chk_diag else 'N/A'}, Sécurité: {'OK' if chk_wipe else 'N/A'}, Test: {'OK' if chk_test else 'N/A'}]"
            )
            
            st.markdown("---")
            commentaire_final = st.text_area("Commentaire / Fiche de Réaffectation", value=default_comment)
            
            if st.form_submit_button("Valider la Réaffectation", use_container_width=True):
                exec_query(
                    "INSERT INTO reaffectations (nom_equipement, mois_annee_acquisition, numero_serie, destination, departement, date_reaffectation, commentaire) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (curr_info['nom_equipement'], curr_info['mois_annee_acquisition'], serie_sel, destination, nouveau_dept, date_reaff, commentaire_final)
                )
                exec_query("UPDATE affectations SET lieu=?, departement=? WHERE numero_serie=?", (destination, nouveau_dept, serie_sel))
                st.success("Réaffectation enregistrée avec succès !")
                st.rerun()

    st.markdown('<div class="blue-cell-box">Tableau des Réaffectations</div>', unsafe_allow_html=True)
    df_re = get_data("SELECT * FROM reaffectations")
    
    if not df_re.empty:
        st.dataframe(df_re, use_container_width=True)
        
        # Bouton pour vider le tableau
        if st.button("🗑️ Vider le tableau des réaffectations", type="primary"):
            if "confirm_reaff_delete" not in st.session_state:
                st.session_state.confirm_reaff_delete = True
            
        if st.session_state.get("confirm_reaff_delete", False):
            st.warning("⚠️ Êtes-vous sûr de vouloir supprimer TOUTES les données de réaffectation ?")
            col_r1, col_r2 = st.columns(2)
            if col_r1.button("Oui, supprimer tout"):
                exec_query("DELETE FROM reaffectations")
                st.session_state.confirm_reaff_delete = False
                st.rerun()
            if col_r2.button("Annuler"):
                st.session_state.confirm_reaff_delete = False
                st.rerun()
    else:
        st.info("Le tableau des réaffectations est vide.")
# --- 5. DÉSAFFECTATION ---
elif menu == "Désaffectation":
    st.title("❌ Désaffectation d'Équipement")
    
    # Commentaire intelligent au-dessus du formulaire
    st.markdown("""
        <div style="padding: 12px 15px; border-radius: 8px; background-color: #f0f4f8; border-left: 5px solid #0066cc; margin-bottom: 20px;">
            <p style="margin: 0; color: #1e293b; font-size: 14px;">
                <b>ℹ️ Guide <span style="color: #ef4444; font-weight: bold;">*</span> :</b> Sélectionnez un équipement actif par son numéro de série. La fiche de désaffectation se remplira automatiquement ci-dessous, prête à être validée et archivée.
            </p>
        </div>
    """, unsafe_allow_html=True)

    df_source = get_data("SELECT * FROM affectations")
    
    if df_source.empty:
        st.warning("Aucun équipement disponible dans les affectations.")
    else:
        serie_desaf = st.selectbox("Sélectionner l'équipement par numéro de série *", df_source['numero_serie'].tolist())
        item_info = df_source[df_source['numero_serie'] == serie_desaf].iloc[0]
        
        # --- EN-TÊTE AVEC TITRE ET COMMENTAIRE DANS UNE CASE STYLISÉE (SANS LOGOS) ---
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; padding: 15px 0;">
                <h4 style="color: #1e3a8a; margin: 0; font-size: 18px; font-weight: 700;">DÉTAILS DE LA DÉSAFFECTATION <span style="color: #ef4444; font-weight: bold;">*</span></h4>
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin: 12px auto 0 auto; max-width: 650px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <p style="color: #475569; font-size: 13px; margin: 0; line-height: 1.5;">
                        <b>📝 Note <span style="color: #ef4444; font-weight: bold;">*</span> :</b> Veuillez vérifier les informations ci-dessous et renseigner les paramètres requis pour acter la mise au rebut ou le déclassement sécurisé de cet équipement informatique.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Boîte de fond stylisée pour le formulaire de validation
        st.markdown('<div class="blue-cell-box" style="margin-top: 25px;">Validation et Paramètres de Désaffectation <span style="color: #ef4444; font-weight: bold;">*</span></div>', unsafe_allow_html=True)
        
        with st.form("form_desaf"):
            col1, col2 = st.columns(2)
            with col1:
                section = st.text_input("Section *", value=item_info['section'])
                motif_rebut = st.selectbox("Motif du déclassement *", [
                    "Panne matérielle irréparable",
                    "Obsolescence technique / Performance insuffisante",
                    "Coût de réparation supérieur à la valeur résiduelle",
                    "Fin de cycle de vie / Renouvellement de parc"
                ])
            with col2:
                mois_annee_desaf = st.text_input("Mois & Année de désaffectation *", value=datetime.date.today().strftime("%B %Y"))
                departement = st.selectbox("Département *", DEPARTEMENTS_LIST)
                
            # Options de sécurité, état de l'équipement et destination finale
            st.markdown("#### 🔒 Sécurité, État et Destination <span style='color: #ef4444; font-weight: bold;'>*</span>", unsafe_allow_html=True)
            col_sec1, col_sec2 = st.columns(2)
            with col_sec1:
                sec_sauvegarde = st.checkbox("Sauvegarde des données critiques effectuée *", value=True)
                sec_effacement = st.checkbox("Effacement sécurisé des données réalisé *", value=True)
                etat_equipement = st.radio("État de l'équipement *", ["En vie", "C'est foutue"])
                
            with col_sec2:
                destination_choix = st.selectbox("Destination finale du matériel *", [
                    "Stock IT",
                    "Conteneur IT",
                    "Personnalisé"
                ])
                
                if destination_choix == "Personnalisé":
                    destination_finale = st.text_input("Précisez la destination personnalisée *")
                else:
                    destination_finale = destination_choix
                
            date_desaf = datetime.date.today().strftime("%Y-%m-%d")
            commentaire_final = st.text_area(
                "Commentaire / Observations *", 
                value=f"Motif: {motif_rebut} | État: {etat_equipement} | Destination: {destination_finale} | Désaffecté le {date_desaf}"
            )
            
            if st.form_submit_button("Valider et Archiver la Désaffectation", use_container_width=True):
                exec_query(
                    "INSERT INTO desaffectations (nom_equipement, section, mois_annee_desaffectation, departement, date_desaffectation, commentaire) VALUES (?, ?, ?, ?, ?, ?)",
                    (item_info['nom_equipement'], section, mois_annee_desaf, departement, date_desaf, commentaire_final)
                )
                exec_query("DELETE FROM affectations WHERE numero_serie=?", (serie_desaf,))
                st.success("Désaffectation enregistrée et archivée avec succès !")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="blue-cell-box">Tableau des Désaffectations <span style="color: #ef4444; font-weight: bold;">*</span></div>', unsafe_allow_html=True)
    df_d = get_data("SELECT * FROM desaffectations")
    
    if not df_d.empty:
        st.dataframe(df_d, width='stretch')
        
        # Bouton pour vider le tableau
        if st.button("🗑️ Vider le tableau des désaffectations", type="primary"):
            if "confirm_delete" not in st.session_state:
                st.session_state.confirm_delete = True
            
        if st.session_state.get("confirm_delete", False):
            st.markdown("""
    <div style="padding: 10px 15px; border-radius: 5px; background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; margin-bottom: 10px;">
        ⚠️ Êtes-vous sûr de vouloir supprimer TOUTES les données de désaffectation ? <span style="color: #ef4444; font-weight: bold;">*</span>
    </div>
""", unsafe_allow_html=True)
            col_v1, col_v2 = st.columns(2)
            if col_v1.button("Oui, supprimer tout"):
                exec_query("DELETE FROM desaffectations")
                st.session_state.confirm_delete = False
                st.rerun()
            if col_v2.button("Annuler"):
                st.session_state.confirm_delete = False
                st.rerun()
    else:
        st.info("Le tableau des désaffectations est vide.")

# --- 6. ÉDITER LE FORMULAIRE ---
elif menu == "Éditer le formulaire":
    st.title("✏️ Édition des Formulaires")
    table_choix = st.selectbox("Choisir la table à éditer", ["entrees_stock", "affectations", "reaffectations", "desaffectations"])
    df_mod = get_data(f"SELECT * FROM {table_choix}")
    
    if not df_mod.empty:
        id_mod = st.selectbox("Sélectionner l'ID", df_mod['id'].tolist())
        row_data = df_mod[df_mod['id'] == id_mod].iloc[0]
        
        with st.form("form_edit"):
            updated_vals = {col: st.text_input(f"Éditer {col}", value=str(row_data[col])) for col in df_mod.columns if col != 'id'}
            if st.form_submit_button("Mettre à jour", use_container_width=True):
                set_clause = ", ".join([f"{c} = ?" for c in updated_vals.keys()])
                exec_query(f"UPDATE {table_choix} SET {set_clause} WHERE id = ?", list(updated_vals.values()) + [id_mod])
                st.success("Modifications enregistrées avec succès !")
    else:
        st.info("Aucune donnée disponible dans cette table.")
# --- 7. RAPPORT GÉNÉRAL & EXPORT PDF (TABLEAUX ÉLARGIS ET LISIBLES) ---
elif menu == "Rapport Général & Export PDF":
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    # --- STYLE CSS AVANCÉ : DÉGRADÉS BLEU CIEL HARMONIEUX ET MINI CARTES ULTRA-COMPACTES ---
    st.markdown("""
        <style>
        .gradient-main-box {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #7dd3fc 100%);
            padding: 10px 15px;
            border-radius: 8px;
            color: white;
            text-align: center;
            font-weight: 700;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        
        /* Cartes KPI réduites, très compactes et minimalistes (plus petites) */
        .kpi-card-mini {
            background: linear-gradient(135deg, #0369a1 0%, #0284c7 50%, #38bdf8 100%);
            padding: 4px 5px;
            border-radius: 4px;
            color: white;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            margin-bottom: 4px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .kpi-card-mini h4 {
            margin: 0;
            font-size: 7px;
            font-weight: 600;
            color: #e0f2fe;
            text-transform: uppercase;
            letter-spacing: 0.2px;
        }
        .kpi-card-mini h2 {
            margin: 1px 0 0 0;
            font-size: 11px;
            font-weight: 800;
            color: #ffffff;
        }

        .executive-summary-box {
            background: linear-gradient(135deg, rgba(2, 132, 199, 0.08), rgba(56, 189, 248, 0.08));
            border-left: 4px solid #0284c7;
            padding: 10px 12px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 12px;
            font-size: 13px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gradient-main-box">📄 Rapport Général & Tableaux Complets du Parc IT</div>', unsafe_allow_html=True)
    
    # --- 1. RÉCUPÉRATION DES DONNÉES DEPUIS LA BASE DE DONNÉES ---
    df_entrees = get_data("SELECT * FROM entrees_stock")
    df_affect = get_data("SELECT * FROM affectations")
    df_reaff = get_data("SELECT * FROM reaffectations")
    df_desaf = get_data("SELECT * FROM desaffectations")
    
    # Calculs métriques supplémentaires pour alimenter les nouvelles cases
    total_flux = len(df_entrees) + len(df_affect) + len(df_reaff) + len(df_desaf)
    taux_affectation = round((len(df_affect) / len(df_entrees) * 100) if len(df_entrees) > 0 else 0, 1)
    
    # --- 2. INDICATEURS CLÉS (KPIS) ULTRA-COMPACTS (6 COLONNES AJOUTÉES) ---
    st.markdown("### 📊 Indicateurs Clés du Parc IT")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f'<div class="kpi-card-mini"><h4>Entrées</h4><h2>{len(df_entrees)}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card-mini"><h4>Affectations</h4><h2>{len(df_affect)}</h2></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card-mini"><h4>Réaffectations</h4><h2>{len(df_reaff)}</h2></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card-mini"><h4>Désaffectations</h4><h2>{len(df_desaf)}</h2></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="kpi-card-mini"><h4>Total Flux</h4><h2>{total_flux}</h2></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="kpi-card-mini"><h4>Taux Aff.</h4><h2>{taux_affectation}%</h2></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # --- 3. LES 10 MINI-DIAGRAMMES STATISTIQUES (AVEC 3 NOUVEAUX GRAPHIQUES MULTICOLORES) ---
    st.markdown("### 📈 Tableaux de Bord & 10 Mini-Indicateurs Graphiques")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        st.markdown("**1. Diagramme en Secteur (Pie)**")
        if not df_affect.empty:
            fig1 = px.pie(df_affect, names='departement', hole=0.3, color_discrete_sequence=px.colors.sequential.Blues)
            fig1.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Données insuffisantes")

        st.markdown("**2. Histogramme A (Services)**")
        if not df_affect.empty:
            fig2 = px.histogram(df_affect, x='departement', color_discrete_sequence=['#0284c7'])
            fig2.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Données insuffisantes")

        st.markdown("**3. Diagramme d'Aire (Area)**")
        fig3 = px.area(x=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], y=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], color_discrete_sequence=['#38bdf8'])
        fig3.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("**8. Diagramme en Rayon (Polar/Radar)**")
        fig8 = px.line_polar(r=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], theta=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], line_close=True, color_discrete_sequence=['#0284c7'])
        fig8.update_traces(fill='toself')
        fig8.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig8, use_container_width=True)

    with col_d2:
        st.markdown("**4. Courbe d'Évolution (Line)**")
        fig4 = px.line(x=['S1', 'S2', 'S3', 'S4'], y=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], markers=True, color_discrete_sequence=['#0369a1'])
        fig4.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("**5. Histogramme B (Flux Globaux)**")
        fig5 = px.histogram(x=['Entrées', 'Affectations', 'Réaffectations', 'Désaffectations'], y=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], color_discrete_sequence=['#7dd3fc'])
        fig5.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown("**6. Diagramme en Donut**")
        fig6 = px.pie(names=['Stock', 'Affecté', 'Hors Service'], values=[len(df_entrees), len(df_affect), len(df_desaf)], hole=0.6, color_discrete_sequence=px.colors.qualitative.Set2)
        fig6.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

        st.markdown("**9. Graphique en Entonnoir (Funnel)**")
        fig9 = px.funnel(y=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], x=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], color_discrete_sequence=px.colors.qualitative.Bold)
        fig9.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

    with col_d3:
        st.markdown("**7. Barres Horizontales (Stats)**")
        fig7 = px.bar(y=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], x=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], orientation='h', color_discrete_sequence=['#0284c7'])
        fig7.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig7, use_container_width=True)

        st.markdown("**10. Graphique en Dispersion (Scatter)**")
        fig10 = px.scatter(x=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], y=[len(df_entrees), len(df_affect), len(df_reaff), len(df_desaf)], size=[max(1, len(df_entrees)), max(1, len(df_affect)), max(1, len(df_reaff)), max(1, len(df_desaf))], color=['Entrées', 'Affect.', 'Réaff.', 'Désaf.'], color_discrete_sequence=px.colors.qualitative.Vivid)
        fig10.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=120, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig10, use_container_width=True)
        
        st.markdown("""
            <div style="background: rgba(2, 132, 199, 0.08); padding: 8px; border-radius: 6px; text-align: center; margin-top: 5px;">
                <span style="font-size: 11px; font-weight: bold; color: #0284c7;">📊 10 Graphiques Multicolores</span><br>
                <span style="font-size: 9px; color: #555;">Intégration de 3 nouveaux diagrammes (Radar, Entonnoir et Dispersion) aux teintes harmonieuses.</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- 4. SYNTHÈSE EXÉCUTIVE AUTOMATIQUE ---
    st.markdown("### 🤖 Synthèse Exécutive Intelligente")
    total_operations = len(df_entrees) + len(df_affect) + len(df_reaff) + len(df_desaf)
    
    auto_insight = f"Le parc informatique enregistre un volume global de {total_operations} opérations réparties sur l'ensemble des flux. "
    if not df_affect.empty:
        top_dept = df_affect['departement'].mode()
        top_dept_str = top_dept.iloc[0] if not top_dept.empty else "Non défini"
        auto_insight += f"Le département le plus actif en affectations est actuellement **{top_dept_str}**."
    else:
        auto_insight += "Aucune affectation majeure recensée pour identifier un pôle dominant."

    st.markdown(f"""
        <div class="executive-summary-box">
            <strong>💡 Analyse automatique des flux :</strong> {auto_insight}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💬 Commentaire & Observations Personnalisées")
    commentaire_rapport = st.text_area("Saisir un commentaire ou une observation pour le rapport...", height=80, placeholder="Ajoutez vos notes spécifiques ici...")

    # --- 5. CLASSE DE GÉNÉRATION PDF (FPDF) ---
    class PDFReport(FPDF):
        def header(self):
            try:
                self.image('itm.png', x=15, y=6, w=25)
            except Exception:
                pass
            try:
                self.image('entreprise.jpg', x=256, y=6, w=25)
            except Exception:
                pass
            self.ln(10)
            self.set_font('Arial', 'B', 14)
            self.cell(0, 8, "RAPPORT GENERAL DU PARC IT", 0, 1, 'C')
            self.ln(4)
            
        def footer(self):
            self.set_y(-20)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(100, 100, 100)
            date_now = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
            user_name = st.session_state.get('user', 'Admin')
            self.cell(0, 4, f"Généré le : {date_now} | Responsable : {user_name} | Département : IT", 0, 1, 'R')
            self.cell(0, 4, "Fait à Kasumbalesa", 0, 0, 'R')

    # Construction du document PDF en format paysage A4 (Les tableaux complets s'impriment exclusivement ici)
    pdf = PDFReport(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()
    pdf.set_font("Arial", size=9)
    
    pdf.cell(0, 5, f"Date d'exportation : {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1)
    if commentaire_rapport:
        pdf.multi_cell(0, 5, f"Observation : {commentaire_rapport}")
    pdf.ln(3)
    
    # Fonction d'insertion des tableaux dynamiques dans le PDF
    def add_table_to_pdf(pdf_obj, title, df_data):
        pdf_obj.set_font("Arial", 'B', 10)
        pdf_obj.cell(0, 6, title.upper(), 0, 1)
        pdf_obj.set_font("Arial", size=8)
        
        if df_data.empty:
            pdf_obj.cell(0, 5, "Aucune donnée enregistrée.", 0, 1)
            pdf_obj.ln(2)
            return
            
        cols = [c for c in df_data.columns if c != 'id'][:6]
        col_w = 42  
        
        pdf_obj.set_fill_color(224, 242, 254)
        for col in cols:
            pdf_obj.cell(col_w, 6, str(col).upper()[:22], 1, 0, 'C', True)
        pdf_obj.ln(6)
        
        pdf_obj.set_font("Arial", size=8)
        for _, row in df_data.iterrows():
            for col in cols:
                cell_value = "" if pd.isna(row[col]) else str(row[col])
                pdf_obj.cell(col_w, 5, cell_value[:24], 1, 0, 'L')
            pdf_obj.ln(5)
        pdf_obj.ln(4)

    add_table_to_pdf(pdf, "1. Entrées Stock IT", df_entrees)
    add_table_to_pdf(pdf, "2. Affectations", df_affect)
    add_table_to_pdf(pdf, "3. Réaffectations", df_reaff)
    add_table_to_pdf(pdf, "4. Désaffectations", df_desaf)
    
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    # --- 6. EXPORTATION ET ENVOI PAR MESSAGERIE DIRECTE ---
    st.markdown("---")
    st.markdown("### 📤 Exportation et Envoi Direct par Mail")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        client_mail = st.selectbox("Choisir la messagerie", ["Gmail", "Outlook"])
        email_expediteur = st.text_input("Adresse e-mail de l'expéditeur")
    with col_m2:
        mot_de_passe_mail = st.text_input("Mot de passe (ou Mot de passe d'application)", type="password")
        email_dest = st.text_input("Adresse e-mail du destinataire")
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.download_button(
            label="📥 Télécharger le Rapport PDF",
            data=pdf_bytes,
            file_name=f"Rapport_Parc_IT_{datetime.date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with col_b2:
        if st.button("🚀 Envoyer le Rapport par E-mail", use_container_width=True):
            if email_expediteur and email_dest and mot_de_passe_mail:
                try:
                    smtp_server = "smtp.gmail.com" if client_mail == "Gmail" else "smtp.office365.com"
                    smtp_port = 465

                    msg = MIMEMultipart()
                    msg['From'] = email_expediteur
                    msg['To'] = email_dest
                    msg['Subject'] = f"📊 Rapport Général du Parc IT - {datetime.date.today().strftime('%d/%m/%Y')}"

                    corps_txt = f"""Bonjour,\n\nVeuillez trouver ci-joint le rapport général du parc informatique généré le {datetime.date.today().strftime('%d/%m/%Y')}.\n\nObservation : {commentaire_rapport if commentaire_rapport else 'Aucune observation particulière.'}\n\nCordialement,\nService IT - Kasumbalesa"""
                    msg.attach(MIMEText(corps_txt, 'plain'))

                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(pdf_bytes)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="Rapport_Parc_IT_{datetime.date.today()}.pdf"')
                    msg.attach(part)

                    with st.spinner("Connexion sécurisée au serveur de messagerie..."):
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                            server.login(email_expediteur, mot_de_passe_mail)
                            server.sendmail(email_expediteur, email_dest, msg.as_string())

                    st.success(f"✅ E-mail envoyé avec succès via {client_mail} !")
                except Exception as e:
                    st.error(f"❌ Erreur d'envoi : {str(e)}")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs : Expéditeur, Mot de passe et Destinataire.")
# --- 8. MESSAGERIE OUTLOOK & GMAIL ---
elif menu == "Messagerie Outlook & Gmail":
    st.title("✉️ Centre de Messagerie Intégré (Outlook & Gmail)")
    
    tab_out, tab_gmail, tab_chat = st.tabs(["Boîte Outlook", "Boîte Gmail", "Chat Interne & Répliques"])
    
    with tab_out:
        st.subheader("Boîte de Réception Outlook")
        folder_out = st.selectbox("Dossiers Outlook", ["Boîte de réception", "Éléments envoyés", "Brouillons", "Archives", "Corbeille"], key="folder_out")
        
        with st.form("form_send_outlook", clear_on_submit=True):
            st.markdown("### 📤 Composer / Détails du message")
            expediteur_mail = st.text_input("Adresse de l'Expéditeur", value=f"{st.session_state.user}@entreprise.com")
            destinataire_mail = st.text_input("Adresse du Destinataire")
            sujet_mail = st.text_input("Sujet du message")
            corps_mail = st.text_area("Corps du Message")
            
            if st.form_submit_button("Envoyer l'e-mail via Outlook", use_container_width=True):
                if destinataire_mail and corps_mail:
                    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    exec_query("INSERT INTO messages_outlook (expediteur, message, date_envoi) VALUES (?, ?, ?)", 
                               (expediteur_mail, f"[À: {destinataire_mail}] [Sujet: {sujet_mail}] - {corps_mail}", date_time))
                    st.success("E-mail envoyé avec succès !")
                    st.rerun()

        st.markdown("### 📥 Historique des messages")
        df_msgs = get_data("SELECT expediteur, message, date_envoi FROM messages_outlook")
        for idx, row in df_msgs.iterrows():
            st.markdown(f"""
                <div style='background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #0284c7; margin-bottom: 6px; border: 1px solid #e2e8f0;'>
                    <small style='color: #64748b;'><b>De :</b> {row['expediteur']} | <b>Date :</b> {row['date_envoi']}</small>
                    <p style='margin-top: 3px; font-size: 13px; color: #0f172a;'>{row['message']}</p>
                </div>
            """, unsafe_allow_html=True)
        
    with tab_gmail:
        st.subheader("Boîte de Réception Gmail")
        label_gmail = st.selectbox("Libellés Gmail", ["Boîte de réception", "Messages suivis", "Envoyés", "Spam", "Corbeille"], key="label_gmail")
        
        with st.form("form_send_gmail", clear_on_submit=True):
            st.markdown("### 📤 Composer / Détails du message")
            expediteur_gmail = st.text_input("Adresse de l'Expéditeur (Gmail)", value=f"{st.session_state.user}@gmail.com")
            destinataire_gmail = st.text_input("Adresse du Destinataire (Gmail)")
            sujet_gmail = st.text_input("Objet du message")
            corps_gmail = st.text_area("Contenu du message")
            
            if st.form_submit_button("Envoyer l'e-mail via Gmail", use_container_width=True):
                if destinataire_gmail and corps_gmail:
                    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    exec_query("INSERT INTO messages_outlook (expediteur, message, date_envoi) VALUES (?, ?, ?)", 
                               (expediteur_gmail, f"[Gmail - À: {destinataire_gmail}] [Objet: {sujet_gmail}] - {corps_gmail}", date_time))
                    st.success("E-mail envoyé avec succès !")
                    st.rerun()

        st.markdown("### 📥 Messages enregistrés")
        for idx, row in df_msgs.iterrows():
            st.markdown(f"""
                <div style='background: white; padding: 10px; border-radius: 6px; border-left: 4px solid #ea4335; margin-bottom: 6px; border: 1px solid #e2e8f0;'>
                    <small style='color: #64748b;'><b>De :</b> {row['expediteur']} | <b>Date :</b> {row['date_envoi']}</small>
                    <p style='margin-top: 3px; font-size: 13px; color: #0f172a;'>{row['message']}</p>
                </div>
            """, unsafe_allow_html=True)
        
    with tab_chat:
        st.subheader("Discussion en direct entre Équipes IT (Bulles rondes)")
        for idx, row in df_msgs.iterrows():
            is_me = (row['expediteur'] == st.session_state.user)
            bubble_class = "chat-bubble-right" if is_me else "chat-bubble-left"
            align_div = "right" if is_me else "left"
            st.markdown(f"""
                <div style='display: flex; justify-content: {align_div}; width: 100%;'>
                    <div class='{bubble_class}'>
                        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 2px;'>
                            <div style='width: 24px; height: 24px; background: #0284c7; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px;'>{row['expediteur'][0].upper()}</div>
                            <small><b>{row['expediteur']}</b> • {row['date_envoi']}</small>
                        </div>
                        <span style='font-size: 13px;'>{row['message']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with st.form("form_chat", clear_on_submit=True):
            exp_chat = st.text_input("Nom / Expéditeur", value=st.session_state.user)
            msg_text = st.text_input("Écrire un message...")
            if st.form_submit_button("Envoyer le message", use_container_width=True) and msg_text:
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                exec_query("INSERT INTO messages_outlook (expediteur, message, date_envoi) VALUES (?, ?, ?)", (exp_chat, msg_text, date_time))
                st.rerun()

# --- 9. PARAMÈTRES ---
elif menu == "Paramètres":
    st.title("⚙️ Paramètres & Sécurité")
    
    # Section 1 : Modifier le mot de passe
    with st.form("form_password"):
        st.subheader("Modifier le mot de passe Administrateur")
        ancien_pwd = st.text_input("Ancien mot de passe", type="password")
        nouveau_pwd = st.text_input("Nouveau mot de passe", type="password")
        confirmer_pwd = st.text_input("Confirmer le nouveau mot de passe", type="password")
        
        if st.form_submit_button("Mettre à jour le mot de passe", use_container_width=True):
            conn = sqlite3.connect("gestion_it.db")
            cur = conn.cursor()
            cur.execute("SELECT valeur FROM config WHERE cle='password'")
            result = cur.fetchone()
            current_db_pwd = result[0] if result else None
            conn.close()
            
            if ancien_pwd == current_db_pwd and nouveau_pwd == confirmer_pwd and nouveau_pwd != "":
                exec_query("UPDATE config SET valeur = ? WHERE cle = 'password'", (nouveau_pwd,))
                st.success("Mot de passe modifié avec succès !")
            else:
                st.error("Erreur : Vérifiez votre ancien mot de passe ou la correspondance des nouveaux.")

    # Section 2 : Modifier le nom d'utilisateur
    st.markdown("---")
    with st.form("form_user"):
        st.subheader("Modifier le nom d'utilisateur")
        # Récupération de l'utilisateur actuel
        current_user = st.session_state.get("user", "Admin")
        nouveau_user = st.text_input("Nouveau nom d'utilisateur", value=current_user)
        
        if st.form_submit_button("Mettre à jour le nom d'utilisateur", use_container_width=True):
            if nouveau_user and nouveau_user != current_user:
                # Mise à jour dans la base de données (si une table users ou config existe)
                # On met à jour la session pour refléter le changement immédiatement
                exec_query("UPDATE config SET valeur = ? WHERE cle = 'username'", (nouveau_user,))
                st.session_state["user"] = nouveau_user
                st.success(f"Nom d'utilisateur mis à jour : {nouveau_user}")
                st.rerun() # Recharger pour appliquer le nom partout
            else:
                st.warning("Veuillez entrer un nom d'utilisateur valide et différent du précédent.")