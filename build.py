"""Construit le site jugeote.fr dans le dossier _site/.

1. Lit le flux RSS du podcast et met à jour data/episodes.json
   (si le flux est injoignable, garde la dernière version connue).
2. Assemble chaque page de pages/ avec l'en-tête et le pied communs.
3. Copie css/ et assets/, puis écrit sitemap.xml, robots.txt et llms.txt.

Lancer : python3 build.py   (aucune dépendance à installer)
"""
import email.utils
import html
import json
import re
import shutil
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).parent
SORTIE = RACINE / '_site'
SITE = 'https://www.jugeote.fr'
RSS = 'https://feeds.podcastics.com/podcastics/podcasts/rss/5923_c0971b47dc884a3018a618a101714dd0.rss'
LIEN_PODCAST = 'https://www.podcastics.com/podcast/5923/link/'
MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
CATEGORIES = ['Coach financier', 'CGP', 'CIF indépendant']


def e(texte):
    return html.escape(texte or '', quote=True)


def date_fr(iso):
    a, m, j = iso.split('-')
    return f'{int(j)} {MOIS[int(m) - 1]} {a}'


# ---------- Épisodes ----------

def lire_rss():
    req = urllib.request.Request(RSS, headers={'User-Agent': 'jugeote-site-build'})
    with urllib.request.urlopen(req, timeout=30) as r:
        racine = ET.fromstring(r.read())
    episodes = []
    for item in racine.iter('item'):
        titre = (item.findtext('title') or '').strip()
        desc = re.sub(r'<[^>]+>', '\n', item.findtext('description') or '')
        m = re.match(r'#?\s*(\d+)\s*[-–:.]\s*(.+)', titre)
        num, titre_court = (m.group(1), m.group(2).strip()) if m else ('', titre)
        inv = re.search(r'Invit[ée]e?s?\s*:\s*([^\n]+)', desc)
        date = item.findtext('pubDate')
        iso = email.utils.parsedate_to_datetime(date).date().isoformat() if date else ''
        episodes.append({
            'num': num,
            'titre': titre_court,
            'invite': inv.group(1).strip() if inv else '',
            'date': iso,
            'lien': (item.findtext('link') or '').strip() or LIEN_PODCAST,
        })
    episodes.sort(key=lambda x: x['date'], reverse=True)
    return episodes


def charger_episodes():
    cache = RACINE / 'data' / 'episodes.json'
    try:
        episodes = lire_rss()
        if episodes:
            cache.write_text(json.dumps(episodes, ensure_ascii=False, indent=1) + '\n')
            print(f'RSS lu : {len(episodes)} épisodes')
            return episodes
    except Exception as err:  # flux injoignable : on garde la dernière version
        print(f'RSS injoignable ({err}), utilisation de data/episodes.json')
    return json.loads(cache.read_text())


def carte_episode(ep):
    invite = f'<p>Avec {e(ep["invite"])}</p>' if ep['invite'] else ''
    num = f'<span class="pastille">#{e(ep["num"])}</span>' if ep['num'] else '<span></span>'
    return (f'<article class="carte">\n<div class="carte-haut">{num}'
            f'<span class="carte-date">{date_fr(ep["date"])}</span></div>\n'
            f'<h3>{e(ep["titre"])}</h3>\n{invite}\n'
            f'<a class="lien-fort" href="{e(ep["lien"])}">Écouter l\'épisode</a>\n</article>')


def ligne_episode(ep):
    meta = date_fr(ep['date']) + (f', avec {e(ep["invite"])}' if ep['invite'] else '')
    return (f'<li><span class="num">{"#" + e(ep["num"]) if ep["num"] else ""}</span>'
            f'<a href="{e(ep["lien"])}">{e(ep["titre"])}</a>'
            f'<span class="meta">{meta}</span></li>')


# ---------- Top Voice ----------

def top_voice():
    donnees = json.loads((RACINE / 'data' / 'top-voice.json').read_text())
    membres = donnees.get('membres', [])
    if not membres:
        return '', f'<p class="message-vide">{e(donnees.get("message_attente", ""))}</p>'
    presentes = [c for c in CATEGORIES if any(m.get('categorie') == c for m in membres)]
    filtres = '<div class="filtres" role="group" aria-label="Filtrer par profil">' + ''.join(
        f'<button type="button" data-cat="{e(c)}" aria-pressed="{"true" if c == "Tous" else "false"}">{e(c)}</button>'
        for c in ['Tous'] + presentes) + '</div>'
    cartes = []
    for m in membres:
        nom = m.get('nom', '')
        if m.get('photo'):
            visuel = f'<img class="membre-photo" src="/assets/top-voice/{e(m["photo"])}" alt="" width="72" height="72">'
        else:
            initiales = ''.join(p[0] for p in nom.split()[:2]).upper()
            visuel = f'<div class="membre-initiales" aria-hidden="true">{e(initiales)}</div>'
        liens = ''
        if m.get('episode'):
            liens += f'<a class="lien-fort" href="{e(m["episode"])}">Son épisode</a>'
        if m.get('site'):
            liens += f'<a class="lien-fort" href="{e(m["site"])}">Son site</a>'
        actif = f'<p class="actif">Partenaire actif jusqu\'en {e(m["actif_jusqu_a"])}</p>\n' if m.get('actif_jusqu_a') else ''
        cartes.append(
            f'<article class="carte" data-categorie="{e(m.get("categorie", ""))}">\n{visuel}\n'
            f'<h3>{e(nom)}</h3>\n<span class="categorie">{e(m.get("categorie", ""))}</span>\n'
            f'<p>{e(m.get("description", ""))}</p>\n{actif}<div class="liens-carte">{liens}</div>\n</article>')
    return filtres, '<div class="grille">\n' + '\n'.join(cartes) + '\n</div>'


# ---------- Assemblage ----------

def construire():
    episodes = charger_episodes()
    filtres, membres = top_voice()
    valeurs = {
        'NB_EPISODES': str(max([int(x['num']) for x in episodes if x['num'].isdigit()] or [len(episodes)])),
        'EPISODES_RECENTS': '\n'.join(carte_episode(x) for x in episodes[:6]),
        'EPISODES_TOUS': '\n'.join(ligne_episode(x) for x in episodes),
        'TOP_VOICE_FILTRES': filtres,
        'TOP_VOICE_MEMBRES': membres,
    }
    entete = (RACINE / 'pages' / '_entete.html').read_text()
    pied = (RACINE / 'pages' / '_pied.html').read_text()

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    shutil.copytree(RACINE / 'css', SORTIE / 'css')
    shutil.copytree(RACINE / 'assets', SORTIE / 'assets')

    chemins = []
    for page in sorted((RACINE / 'pages').glob('[!_]*.html')):
        source = page.read_text()
        meta = dict(re.findall(r'^(TITRE|DESCRIPTION|CHEMIN):[ \t]*(.*)$', source, re.M))
        corps = re.sub(r'^<!--.*?-->\n', '', source, count=1, flags=re.S)
        actif = {'episodes.html': 'EPISODES', 'top-voice.html': 'TOPVOICE', 'a-propos.html': 'APROPOS'}
        tete = entete
        for fichier, cle in actif.items():
            tete = tete.replace('{{ACTIF_' + cle + '}}', ' aria-current="page"' if page.name == fichier else '')
        for cle in ('TITRE', 'DESCRIPTION', 'CHEMIN'):
            tete = tete.replace('{{' + cle + '}}', e(meta.get(cle, '')))
        contenu = tete + corps + pied
        for cle, val in valeurs.items():
            contenu = contenu.replace('{{' + cle + '}}', val)
        reste = re.findall(r'\{\{[A-Z_]+\}\}', contenu)
        if reste:
            raise SystemExit(f'{page.name} : balise inconnue {reste}')
        (SORTIE / page.name).write_text(contenu)
        chemins.append(meta.get('CHEMIN', ''))

    (SORTIE / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'<url><loc>{SITE}/{c}</loc></url>\n' for c in chemins) + '</urlset>\n')
    (SORTIE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    (SORTIE / 'llms.txt').write_text(
        '# Jugeote\n\n> Podcast francophone d\'interviews sur les finances personnelles : Bourse, ETF, '
        'immobilier, SCPI, épargne. Un épisode chaque mardi, animé par David.\n\n'
        f'- [Tous les épisodes]({SITE}/episodes.html)\n- [Top Voice Jugeote]({SITE}/top-voice.html)\n'
        f'- [À propos et contact]({SITE}/a-propos.html)\n- [Newsletter](https://newsletter.jugeote.fr)\n\n'
        '## Derniers épisodes\n\n'
        + ''.join(f'- #{x["num"]} {x["titre"]}' + (f' (avec {x["invite"]})' if x['invite'] else '') + f': {x["lien"]}\n'
                  for x in episodes[:30]))
    (SORTIE / '.nojekyll').write_text('')
    print(f'Site construit dans {SORTIE}')


if __name__ == '__main__':
    construire()
