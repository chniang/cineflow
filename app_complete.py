import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
from pathlib import Path
from datetime import datetime
import re
import sqlite3

# -------------------------
# CONFIGURATION
# -------------------------

st.set_page_config(
    page_title="CineFlow",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------
# RESPONSIVE CSS
# -------------------------
def load_css():
    """Charge le CSS responsive"""
    try:
        with open('style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Charger CSS
load_css()

# Initialiser le state pour la navigation
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

# Utiliser SQLite
DB_PATH = Path(__file__).parent / "tidiane_flix.db"
SQLALCHEMY_URL = f"sqlite:///{DB_PATH}"

# -------------------------
# UTILITAIRES DB
# -------------------------

@st.cache_resource
def get_engine(url=SQLALCHEMY_URL):
    return create_engine(url, pool_pre_ping=True)

@st.cache_data(ttl=60)
def run_query(query, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    return df

_ALLOWED_TABLES = {"client", "film", "salle", "projection", "ticket", "avis"}

@st.cache_data(ttl=60)
def get_table(table_name, limit=1000):
    if table_name not in _ALLOWED_TABLES:
        raise ValueError(f"Table non autorisée : {table_name!r}")
    q = f"SELECT * FROM {table_name} LIMIT :limit"
    return run_query(q, {'limit': limit})

def insert_ticket(prix, date_achat, id_client, id_projection):
    engine = get_engine()
    insert_sql = text("""
        INSERT INTO ticket (prix, date_achat, id_client, id_projection)
        VALUES (:prix, :date_achat, :id_client, :id_projection)
    """)
    with engine.begin() as conn:
        res = conn.execute(insert_sql, {
            'prix': float(prix),
            'date_achat': date_achat,
            'id_client': int(id_client),
            'id_projection': int(id_projection)
        })
        ticket_id = res.lastrowid if hasattr(res, "lastrowid") else None
    run_query.clear()
    get_table.clear()
    return ticket_id

# -------------------------
# LANDING PAGE
# -------------------------

def show_landing_page():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {background: linear-gradient(180deg, #141414 0%, #000000 100%);}
        
        .hero {
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(180deg, rgba(229,9,20,0.1) 0%, transparent 100%);
        }
        .hero-title {
            font-size: 72px;
            font-weight: 900;
            color: #E50914;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
            margin-bottom: 20px;
        }
        .hero-subtitle {
            font-size: 28px;
            color: #ffffff;
            margin-bottom: 40px;
        }
        .feature-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 40px;
            margin: 20px;
            text-align: center;
            transition: all 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-10px);
            background: rgba(255,255,255,0.08);
            border-color: #E50914;
        }
        .custom-footer {
            text-align: center;
            padding: 40px;
            color: #808080;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 80px;
        }

        /* Responsive mobile pour la landing page */
        @media screen and (max-width: 768px) {
            .hero-title {
                font-size: 2rem !important;
                line-height: 1.2 !important;
            }
            .hero-subtitle {
                font-size: 1.2rem !important;
                line-height: 1.4 !important;
            }
            .hero-description {
                font-size: 0.9rem !important;
                padding: 0 1rem !important;
            }
            .cta-button {
                font-size: 1rem !important;
                padding: 12px 24px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
        <div class="hero-title">🎬 CINEFLOW</div>
        <div class="hero-subtitle">Votre cinéma premium à Dakar</div>
        <p style="color: #b3b3b3; font-size: 18px; max-width: 600px; margin: 0 auto 40px;">
            Vivez une expérience cinématographique incomparable avec les derniers blockbusters,
            des salles confortables et un système de réservation moderne.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎫 ACCÉDER AU SYSTÈME DE GESTION", key="cta", use_container_width=True, type="primary"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 64px;">🎥</div>
            <div style="font-size: 24px; color: white; font-weight: bold; margin: 20px 0 15px;">15 Films</div>
            <div style="color: #b3b3b3;">Les derniers blockbusters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 64px;">🏟️</div>
            <div style="font-size: 24px; color: white; font-weight: bold; margin: 20px 0 15px;">3 Salles</div>
            <div style="color: #b3b3b3;">Équipées Dolby Atmos 4K</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 64px;">💺</div>
            <div style="font-size: 24px; color: white; font-weight: bold; margin: 20px 0 15px;">350 Places</div>
            <div style="color: #b3b3b3;">Sièges confortables premium</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 64px;">🎟️</div>
            <div style="font-size: 24px; color: white; font-weight: bold; margin: 20px 0 15px;">Réservation</div>
            <div style="color: #b3b3b3;">Billetterie moderne en ligne</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<br><br><h2 style="color: white; padding-left: 20px;">🍿 Films à l\'affiche</h2>', unsafe_allow_html=True)
    
    films = [
        {"titre": "Inception", "genre": "Science-fiction", "emoji": "🌀"},
        {"titre": "Avengers: Endgame", "genre": "Action", "emoji": "⚡"},
        {"titre": "Titanic", "genre": "Drame", "emoji": "🚢"},
        {"titre": "The Matrix", "genre": "Sci-fi", "emoji": "🔴"},
        {"titre": "Joker", "genre": "Drame", "emoji": "🃏"},
        {"titre": "Parasite", "genre": "Thriller", "emoji": "🎭"},
    ]
    
    cols = st.columns(3)
    for idx, film in enumerate(films):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; 
                        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 48px; text-align: center; margin-bottom: 10px;">{film['emoji']}</div>
                <div style="color: white; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 5px;">
                    {film['titre']}
                </div>
                <div style="color: #E50914; text-align: center; font-size: 14px;">
                    {film['genre']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="custom-footer">
        <p><strong>CineFlow</strong> - Cinéma Premium Dakar</p>
        <p>📍 Dakar, Sénégal | 📞 +221 77 636 27 14 | 📧 cheikhniang159@gmail.com</p>
        <p style="margin-top: 20px; font-size: 14px;">
            © 2025 CineFlow. Tous droits réservés.<br>
            Développé avec ❤️ par Cheikh Niang
        </p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# APPLICATION PRINCIPALE
# -------------------------

def sidebar_navigation():
    st.sidebar.title('🎬 CineFlow')
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🏠 Retour à l'accueil", use_container_width=True):
        st.session_state.show_landing = True
        st.rerun()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio('Navigation', [
        'Analytics Avancés', 'Prédictions ML', 'Dashboard',
        'Films', 'Projections', 'Clients', 'Billets',
        'Vendre un ticket', 'SQL brut'
    ])
    return page

def show_header():
    st.title('🎬 CineFlow — Tableau de bord')
    st.write('Interface complète pour la gestion de billetterie cinéma.')

def page_dashboard():
    show_header()
    st.markdown('**Bienvenue** — Utilisez le menu latéral pour naviguer.')

    col1, col2, col3 = st.columns(3)

    try:
        total_films = run_query('SELECT COUNT(*) as n FROM film').iloc[0]['n']
        total_clients = run_query('SELECT COUNT(*) as n FROM client').iloc[0]['n']
        total_tickets = run_query('SELECT COUNT(*) as n FROM ticket').iloc[0]['n']
    except Exception as e:
        st.error(f"Erreur de connexion DB: {e}")
        return

    col1.metric("Films", total_films, "🎥")
    col2.metric("Clients", total_clients, "👥")
    col3.metric("Billets vendus", total_tickets, "🎟️")

    st.subheader("📅 Dernières projections")
    dfp = run_query("""
        SELECT p.id_projection, p.date_projection, p.heure,
               f.titre, s.nom_salle
        FROM projection p
        JOIN film f ON p.id_film = f.id_film
        JOIN salle s ON p.id_salle = s.id_salle
        ORDER BY p.date_projection DESC LIMIT 10
    """)
    st.dataframe(dfp, use_container_width=True)

def page_films():
    st.header("🎥 Films")
    df = get_table("film")
    st.dataframe(df, use_container_width=True)

def page_projections():
    st.header("🕐 Projections")
    df = run_query("""
        SELECT p.id_projection, p.date_projection, p.heure,
               f.titre, s.nom_salle
        FROM projection p
        JOIN film f ON p.id_film = f.id_film
        JOIN salle s ON p.id_salle = s.id_salle
        ORDER BY p.date_projection, p.heure
    """)
    st.dataframe(df, use_container_width=True)

    st.subheader("🔍 Filtrer par film")
    films = run_query("SELECT id_film, titre FROM film")
    options = {row.id_film: row.titre for _, row in films.iterrows()}

    film_id = st.selectbox("Choisir un film", [None] + list(options.keys()),
                           format_func=lambda x: options.get(x, "—") if x else "— Tous les films —")

    if film_id:
        df2 = run_query("SELECT * FROM projection WHERE id_film = :id", {"id": film_id})
        st.subheader("Résultats filtrés")
        st.dataframe(df2, use_container_width=True)

def page_sell_ticket():
    st.header("💳 Vendre un ticket")

    clients = run_query("SELECT id_client, nom, prenom FROM client")
    clients["label"] = clients["nom"] + " " + clients["prenom"]

    client_id = st.selectbox(
        "Client",
        [None] + clients.id_client.tolist(),
        format_func=lambda x: clients.loc[clients.id_client == x, "label"].values[0]
        if x else "— Sélectionner un client —"
    )

    projections = run_query("""
        SELECT p.id_projection, p.date_projection, p.heure, f.titre
        FROM projection p JOIN film f ON p.id_film = f.id_film
        ORDER BY p.date_projection DESC
    """)
    projections["label"] = projections["titre"] + " — " + projections["date_projection"].astype(str)

    proj_id = st.selectbox(
        "Projection",
        [None] + projections.id_projection.tolist(),
        format_func=lambda x: projections.loc[projections.id_projection == x, "label"].values[0]
        if x else "— Sélectionner une projection —"
    )

    prix = st.number_input("Prix (FCFA)", 1000.0, 100000.0, 3000.0, 500.0)
    date_achat = st.date_input("Date d'achat", datetime.now().date())

    if st.button("💰 Enregistrer", type="primary", use_container_width=True):
        if not client_id or not proj_id:
            st.error("⚠️ Veuillez sélectionner un client et une projection.")
        else:
            tid = insert_ticket(prix, date_achat, client_id, proj_id)
            st.success(f"✅ Billet enregistré (ID: {tid})")
            st.balloons()

def page_clients():
    st.header("👥 Clients")
    df = get_table("client")
    st.dataframe(df, use_container_width=True)

def page_tickets():
    st.header("🎟️ Billets")
    df = run_query("""
        SELECT t.id_ticket, t.prix, t.date_achat,
               c.nom, c.prenom, f.titre
        FROM ticket t
        JOIN client c ON t.id_client = c.id_client
        JOIN projection p ON t.id_projection = p.id_projection
        JOIN film f ON p.id_film = f.id_film
        ORDER BY t.date_achat DESC
        LIMIT 500
    """)
    st.dataframe(df, use_container_width=True)

def page_analytics():
    st.header("📊 Analytics Avancés — Insights Business")
    
    st.info("💡 Analyse approfondie des performances et KPIs du cinéma")
    
    # KPIs Section
    st.subheader("💰 KPIs Financiers")
    
    col1, col2, col3, col4 = st.columns(4)
    
    revenu_total = run_query("SELECT SUM(prix) as total FROM ticket").iloc[0]['total']
    col1.metric("Revenu Total", f"{revenu_total:,.0f} FCFA", "💵")
    
    revenu_moyen = run_query("SELECT AVG(prix) as moyenne FROM ticket").iloc[0]['moyenne']
    col2.metric("Prix Moyen Ticket", f"{revenu_moyen:,.0f} FCFA", "🎫")
    
    tickets_par_client = run_query("""
        SELECT COUNT(*) * 1.0 / COUNT(DISTINCT id_client) as moyenne
        FROM ticket
    """).iloc[0]['moyenne']
    col3.metric("Tickets/Client", f"{tickets_par_client:.1f}", "👤")
    
    occupation = run_query("""
        SELECT COUNT(t.id_ticket) * 100.0 / 
               (COUNT(DISTINCT p.id_projection) * 
                (SELECT AVG(capacite) FROM salle)) as taux
        FROM ticket t
        JOIN projection p ON t.id_projection = p.id_projection
    """).iloc[0]['taux']
    col4.metric("Taux Occupation", f"{occupation:.1f}%", "🏟️")
    
    st.markdown("---")
    
    # Segmentation clients
    st.subheader("👥 Segmentation Clients")
    
    df_clients_seg = run_query("""
        SELECT 
            c.id_client,
            c.nom || ' ' || c.prenom as client,
            COUNT(t.id_ticket) as nb_tickets,
            SUM(t.prix) as total_depense,
            AVG(t.prix) as prix_moyen
        FROM client c
        LEFT JOIN ticket t ON c.id_client = t.id_client
        GROUP BY c.id_client
        ORDER BY total_depense DESC
    """)
    
    def categorize_client(row):
        if row['nb_tickets'] == 0:
            return "Inactif"
        elif row['total_depense'] >= 10000:
            return "VIP 🌟"
        elif row['total_depense'] >= 5000:
            return "Fidèle 💎"
        else:
            return "Occasionnel 🎫"
    
    df_clients_seg['Catégorie'] = df_clients_seg.apply(categorize_client, axis=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        cat_counts = df_clients_seg['Catégorie'].value_counts()
        fig_cat = px.pie(values=cat_counts.values, names=cat_counts.index,
                         title="Distribution des Catégories de Clients")
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        st.markdown("**🏆 Top 10 Clients**")
        top_clients = df_clients_seg.head(10)[['client', 'nb_tickets', 'total_depense', 'Catégorie']]
        st.dataframe(top_clients, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Analyse temporelle
    st.subheader("📈 Tendances Temporelles")
    
    df_temporal = run_query("""
        SELECT 
            date_achat,
            COUNT(*) as nb_ventes,
            SUM(prix) as revenu_jour
        FROM ticket
        GROUP BY date_achat
        ORDER BY date_achat
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ventes = px.line(df_temporal, x='date_achat', y='nb_ventes',
                             title="Évolution des Ventes (nombre de tickets)",
                             markers=True)
        st.plotly_chart(fig_ventes, use_container_width=True)
    
    with col2:
        fig_revenu = px.line(df_temporal, x='date_achat', y='revenu_jour',
                             title="Évolution du Revenu Journalier",
                             markers=True)
        st.plotly_chart(fig_revenu, use_container_width=True)
    
    st.markdown("---")
    
    # Performance des salles
    st.subheader("🏟️ Performance des Salles")
    
    df_salles_perf = run_query("""
        SELECT 
            s.nom_salle,
            s.capacite,
            COUNT(DISTINCT p.id_projection) as nb_projections,
            COUNT(t.id_ticket) as tickets_vendus,
            SUM(t.prix) as revenu,
            ROUND(COUNT(t.id_ticket) * 100.0 / 
                  (s.capacite * COUNT(DISTINCT p.id_projection)), 1) as taux_occupation
        FROM salle s
        LEFT JOIN projection p ON s.id_salle = p.id_salle
        LEFT JOIN ticket t ON p.id_projection = t.id_projection
        GROUP BY s.id_salle
        ORDER BY revenu DESC
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_salle_revenu = px.bar(df_salles_perf, x='nom_salle', y='revenu',
                                   title="Revenu par Salle",
                                   text='revenu')
        st.plotly_chart(fig_salle_revenu, use_container_width=True)
    
    with col2:
        fig_salle_occupation = px.bar(df_salles_perf, x='nom_salle', y='taux_occupation',
                                       title="Taux d'Occupation par Salle (%)",
                                       text='taux_occupation')
        fig_salle_occupation.add_hline(y=70, line_dash="dash", line_color="green",
                                        annotation_text="Objectif 70%")
        st.plotly_chart(fig_salle_occupation, use_container_width=True)
    
    st.markdown("**📋 Détails par Salle**")
    st.dataframe(df_salles_perf, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Insights actionnables
    st.subheader("💡 Insights & Recommandations")
    
    insights = []
    
    best_day = df_temporal.loc[df_temporal['nb_ventes'].idxmax()]
    insights.append(f"📅 **Meilleur jour** : {best_day['date_achat']} avec {int(best_day['nb_ventes'])} tickets vendus")
    
    min_occupation = df_salles_perf.loc[df_salles_perf['taux_occupation'].idxmin()]
    if min_occupation['taux_occupation'] < 50:
        insights.append(f"⚠️ **Optimisation** : {min_occupation['nom_salle']} est sous-utilisée ({min_occupation['taux_occupation']:.1f}% occupation)")
    
    top_film = run_query("""
        SELECT f.titre, COUNT(t.id_ticket) as tickets
        FROM film f
        JOIN projection p ON f.id_film = p.id_film
        JOIN ticket t ON p.id_projection = t.id_projection
        GROUP BY f.id_film
        ORDER BY tickets DESC
        LIMIT 1
    """)
    if not top_film.empty:
        insights.append(f"🎬 **Film le plus populaire** : {top_film.iloc[0]['titre']} ({int(top_film.iloc[0]['tickets'])} tickets)")
    
    nb_vip = len(df_clients_seg[df_clients_seg['Catégorie'] == 'VIP 🌟'])
    if nb_vip > 0:
        insights.append(f"⭐ **Clients VIP** : {nb_vip} clients génèrent les revenus les plus élevés - envisager un programme de fidélité")
    
    for insight in insights:
        st.info(insight)

def page_predictions():
    st.header("🔮 Prédictions ML — Intelligence Artificielle")
    
    st.info("💡 Cette page utilise des modèles de Machine Learning pour prédire les tendances futures")
    
    from sklearn.linear_model import LinearRegression
    import numpy as np
    
    # Prédiction des ventes futures
    st.subheader("📈 Prédiction des Ventes Futures")
    
    df_temporal = run_query("""
        SELECT 
            date_achat,
            COUNT(*) as nb_ventes,
            SUM(prix) as revenu_jour
        FROM ticket
        GROUP BY date_achat
        ORDER BY date_achat
    """)
    
    if len(df_temporal) >= 5:
        df_temporal['date_num'] = pd.to_datetime(df_temporal['date_achat']).astype(np.int64) // 10**9
        
        X = df_temporal[['date_num']].values
        y_ventes = df_temporal['nb_ventes'].values
        y_revenu = df_temporal['revenu_jour'].values
        
        model_ventes = LinearRegression()
        model_ventes.fit(X, y_ventes)
        
        model_revenu = LinearRegression()
        model_revenu.fit(X, y_revenu)
        
        last_date = pd.to_datetime(df_temporal['date_achat'].iloc[-1])
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=7)
        future_dates_num = future_dates.astype(np.int64).values.reshape(-1, 1) // 10**9
        
        pred_ventes = model_ventes.predict(future_dates_num)
        pred_revenu = model_revenu.predict(future_dates_num)
        
        df_pred = pd.DataFrame({
            'Date': future_dates,
            'Ventes Prédites': np.maximum(pred_ventes, 0).round().astype(int),
            'Revenu Prédit (FCFA)': np.maximum(pred_revenu, 0).round().astype(int)
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔮 Prédictions pour les 7 prochains jours**")
            st.dataframe(df_pred, use_container_width=True, hide_index=True)
            
            avg_ventes = df_pred['Ventes Prédites'].mean()
            avg_revenu = df_pred['Revenu Prédit (FCFA)'].mean()
            st.metric("Ventes Moy. Prévues", f"{avg_ventes:.1f} tickets/jour")
            st.metric("Revenu Moy. Prévu", f"{avg_revenu:,.0f} FCFA/jour")
        
        with col2:
            fig_pred = px.line(df_temporal, x='date_achat', y='nb_ventes',
                              title="Ventes Historiques + Prédictions",
                              labels={'date_achat': 'Date', 'nb_ventes': 'Nombre de ventes'})
            
            fig_pred.add_scatter(x=df_pred['Date'], y=df_pred['Ventes Prédites'],
                                mode='lines+markers', name='Prédictions',
                                line=dict(color='red', dash='dash'))
            
            st.plotly_chart(fig_pred, use_container_width=True)
    else:
        st.warning("⚠️ Pas assez de données historiques pour faire des prédictions fiables (min 5 jours)")
    
    st.markdown("---")
    
    # Recommandations de films similaires
    st.subheader("🎬 Système de Recommandation de Films")
    
    df_films = run_query("SELECT id_film, titre, genre FROM film")
    
    selected_film = st.selectbox(
        "Choisir un film",
        df_films['titre'].tolist()
    )
    
    if selected_film:
        film_genre = df_films[df_films['titre'] == selected_film]['genre'].iloc[0]
        
        recommendations = df_films[
            (df_films['genre'] == film_genre) & 
            (df_films['titre'] != selected_film)
        ]
        
        if not recommendations.empty:
            st.success(f"✅ Films similaires à **{selected_film}** ({film_genre}) :")
            
            cols = st.columns(min(3, len(recommendations)))
            for idx, (_, film) in enumerate(recommendations.head(3).iterrows()):
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; 
                                border-radius: 8px; text-align: center; border: 1px solid rgba(229,9,20,0.3);">
                        <div style="font-size: 48px; margin-bottom: 10px;">🎬</div>
                        <div style="color: white; font-size: 18px; font-weight: bold;">{film['titre']}</div>
                        <div style="color: #E50914; font-size: 14px; margin-top: 5px;">{film['genre']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Aucun film similaire trouvé dans la base")
    
    st.markdown("---")
    
    # Scoring clients
    st.subheader("💡 Scoring Clients — Probabilité de Réachat")
    
    df_clients_scoring = run_query("""
        SELECT 
            c.id_client,
            c.nom || ' ' || c.prenom as client,
            COUNT(t.id_ticket) as nb_tickets,
            SUM(t.prix) as total_depense,
            MAX(t.date_achat) as derniere_visite,
            julianday('now') - julianday(MAX(t.date_achat)) as jours_depuis_derniere_visite
        FROM client c
        LEFT JOIN ticket t ON c.id_client = t.id_client
        GROUP BY c.id_client
        HAVING nb_tickets > 0
        ORDER BY jours_depuis_derniere_visite
    """)
    
    if not df_clients_scoring.empty:
        df_clients_scoring['score_fidelite'] = (
            (df_clients_scoring['nb_tickets'] * 20) +
            (100 / (df_clients_scoring['jours_depuis_derniere_visite'] + 1))
        ).round(1)
        
        max_score = df_clients_scoring['score_fidelite'].max()
        df_clients_scoring['proba_reachat'] = (
            (df_clients_scoring['score_fidelite'] / max_score) * 100
        ).round(1)
        
        def categorize_proba(proba):
            if proba >= 70:
                return "🟢 Élevée"
            elif proba >= 40:
                return "🟡 Moyenne"
            else:
                return "🔴 Faible"
        
        df_clients_scoring['Risque'] = df_clients_scoring['proba_reachat'].apply(categorize_proba)
        
        at_risk = df_clients_scoring[df_clients_scoring['proba_reachat'] < 40].head(5)
        high_value = df_clients_scoring[df_clients_scoring['proba_reachat'] >= 70].head(5)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⚠️ Clients à Risque (à réactiver)**")
            if not at_risk.empty:
                st.dataframe(
                    at_risk[['client', 'nb_tickets', 'jours_depuis_derniere_visite', 'proba_reachat']],
                    use_container_width=True,
                    hide_index=True
                )
                st.info("💡 Action : Envoyer une offre promotionnelle pour réengager ces clients")
            else:
                st.success("✅ Aucun client à risque détecté")
        
        with col2:
            st.markdown("**⭐ Clients Fidèles (forte probabilité de réachat)**")
            if not high_value.empty:
                st.dataframe(
                    high_value[['client', 'nb_tickets', 'jours_depuis_derniere_visite', 'proba_reachat']],
                    use_container_width=True,
                    hide_index=True
                )
                st.success("💡 Action : Programme VIP ou réductions exclusives")
            else:
                st.warning("Aucun client avec probabilité élevée")
        
        st.markdown("**📊 Distribution des Probabilités de Réachat**")
        fig_proba = px.histogram(df_clients_scoring, x='proba_reachat', nbins=20,
                                 title="Répartition des scores de fidélité clients",
                                 labels={'proba_reachat': 'Probabilité de réachat (%)'})
        st.plotly_chart(fig_proba, use_container_width=True)
    else:
        st.warning("⚠️ Aucune donnée de tickets disponible pour le scoring")
    
    st.markdown("---")
    
    # Optimisation occupation
    st.subheader("🏟️ Optimisation de l'Occupation des Salles")
    
    df_occupation = run_query("""
        SELECT 
            s.nom_salle,
            s.capacite,
            COUNT(DISTINCT p.id_projection) as nb_projections,
            COUNT(t.id_ticket) as tickets_vendus,
            ROUND(COUNT(t.id_ticket) * 100.0 / 
                  (s.capacite * COUNT(DISTINCT p.id_projection)), 1) as taux_occupation,
            ROUND(s.capacite * 0.7, 0) as objectif_70
        FROM salle s
        LEFT JOIN projection p ON s.id_salle = p.id_salle
        LEFT JOIN ticket t ON p.id_projection = t.id_projection
        GROUP BY s.id_salle
    """)
    
    if not df_occupation.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_opt = px.bar(df_occupation, x='nom_salle', 
                            y=['taux_occupation'],
                            title="Taux d'Occupation Actuel vs Objectif (70%)",
                            labels={'value': 'Taux (%)', 'nom_salle': 'Salle'})
            fig_opt.add_hline(y=70, line_dash="dash", line_color="green",
                             annotation_text="Objectif 70%")
            st.plotly_chart(fig_opt, use_container_width=True)
        
        with col2:
            st.markdown("**💡 Recommandations**")
            for _, salle in df_occupation.iterrows():
                if salle['taux_occupation'] < 50:
                    st.warning(f"**{salle['nom_salle']}** : {salle['taux_occupation']}% - Sous-utilisée")
                elif salle['taux_occupation'] >= 70:
                    st.success(f"**{salle['nom_salle']}** : {salle['taux_occupation']}% - Objectif atteint ! 🎉")
                else:
                    st.info(f"**{salle['nom_salle']}** : {salle['taux_occupation']}% - Proche de l'objectif")

def page_sql_raw():
    st.header("🛠️ SQL brut")
    sql = st.text_area("Requête SELECT", height=150)
    if st.button("▶️ Exécuter", type="primary"):
        s = sql.strip()
        if not s.lower().startswith("select"):
            st.error("⚠️ Uniquement les requêtes SELECT sont autorisées.")
        elif re.search(r';\s*\S', s):
            st.error("⚠️ Requêtes empilées interdites (';' détecté).")
        else:
            try:
                con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
                df = pd.read_sql_query(s, con)
                con.close()
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

# -------------------------
# MAIN
# -------------------------

def main():
    if st.session_state.show_landing:
        show_landing_page()
    else:
        page = sidebar_navigation()

        if page == "Dashboard":
            page_dashboard()
        elif page == "Films":
            page_films()
        elif page == "Projections":
            page_projections()
        elif page == "Vendre un ticket":
            page_sell_ticket()
        elif page == "Clients":
            page_clients()
        elif page == "Billets":
            page_tickets()
        elif page == "Analytics Avancés":
            page_analytics()
        elif page == "Prédictions ML":
            page_predictions()
        elif page == "SQL brut":
            page_sql_raw()

if __name__ == "__main__":
    main()


