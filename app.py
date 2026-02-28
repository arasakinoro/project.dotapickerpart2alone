import streamlit as st
import requests
from collections import defaultdict
import time

# ==========================================
# СЛОВАРЬ РОЛЕЙ ГЕРОЕВ (позиции 1–5)
# ==========================================
hero_roles = {
    "Abaddon": [1, 3, 4, 5],
    "Alchemist": [1],
    "Ancient Apparition": [4, 5],
    "Anti-Mage": [1],
    "Arc Warden": [2],
    "Axe": [3],
    "Bane": [4, 5],
    "Batrider": [2, 3, 4],
    "Beastmaster": [2, 3],
    "Bloodseeker": [1],
    "Bounty Hunter": [4, 5],
    "Brewmaster": [3],
    "Bristleback": [3],
    "Broodmother": [1, 2],
    "Centaur Warrunner": [3],
    "Chaos Knight": [1, 3],
    "Chen": [5],
    "Clinkz": [1],
    "Clockwerk": [4],
    "Crystal Maiden": [4, 5],
    "Dark Seer": [3],
    "Dark Willow": [4, 5],
    "Dawnbreaker": [3],
    "Dazzle": [4, 5],
    "Death Prophet": [3],
    "Disruptor": [4, 5],
    "Doom": [3],
    "Dragon Knight": [1, 2, 3],
    "Drow Ranger": [1],
    "Earth Spirit": [2, 4],
    "Earthshaker": [2, 3, 4],
    "Elder Titan": [4, 5],
    "Ember Spirit": [2],
    "Enchantress": [4, 5],
    "Enigma": [4, 5],
    "Faceless Void": [1],
    "Grimstroke": [4, 5],
    "Gyrocopter": [1],
    "Hoodwink": [4, 5],
    "Huskar": [2, 3],
    "Invoker": [2, 4, 5],
    "Io": [5],
    "Jakiro": [4, 5],
    "Juggernaut": [1],
    "Keeper of the Light": [2, 4, 5],
    "Kez": [1, 2],
    "Kunkka": [2, 3],
    "Legion Commander": [3],
    "Leshrac": [2],
    "Lich": [4, 5],
    "Lifestealer": [1],
    "Lina": [1, 2, 4, 5],
    "Lion": [4, 5],
    "Lone Druid": [2, 3],
    "Luna": [1],
    "Lycan": [3],
    "Magnus": [3, 4],
    "Marci": [2, 4, 5],
    "Mars": [3],
    "Medusa": [1],
    "Meepo": [2],
    "Mirana": [4, 5],
    "Monkey King": [1, 2],
    "Morphling": [1],
    "Muerta": [1],
    "Naga Siren": [1],
    "Nature's Prophet": [1, 2, 4, 5],
    "Necrophos": [2, 3],
    "Night Stalker": [3],
    "Nyx Assassin": [4, 5],
    "Ogre Magi": [4, 5],
    "Omniknight": [3, 5],
    "Oracle": [4, 5],
    "Outworld Destroyer": [2],
    "Pangolier": [2, 3],
    "Phantom Assassin": [1],
    "Phantom Lancer": [1],
    "Phoenix": [3, 4, 5],
    "Primal Beast": [3],
    "Puck": [2],
    "Pudge": [3, 4, 5],
    "Pugna": [4, 5],
    "Queen of Pain": [2],
    "Razor": [1, 3],
    "Riki": [2, 1],
    "Ringmaster": [4, 5],
    "Rubick": [2, 4],
    "Sand King": [3],
    "Shadow Demon": [4, 5],
    "Shadow Fiend": [1, 2],
    "Shadow Shaman": [4, 5],
    "Silencer": [4, 5],
    "Skywrath Mage": [2, 4, 5],
    "Slardar": [3],
    "Slark": [1],
    "Snapfire": [4, 5],
    "Sniper": [2, 4],
    "Spectre": [1],
    "Spirit Breaker": [3, 4],
    "Storm Spirit": [2],
    "Sven": [1],
    "Techies": [4, 5],
    "Templar Assassin": [1, 2],
    "Terrorblade": [1],
    "Tidehunter": [3],
    "Timbersaw": [3],
    "Tinker": [2],
    "Tiny": [2, 4, 3],
    "Treant Protector": [5],
    "Troll Warlord": [1],
    "Tusk": [4, 5],
    "Underlord": [3],
    "Undying": [4, 5],
    "Ursa": [1],
    "Vengeful Spirit": [4, 5],
    "Venomancer": [4, 5],
    "Viper": [2, 3],
    "Visage": [3],
    "Void Spirit": [2],
    "Warlock": [4, 5],
    "Weaver": [1, 4],
    "Windranger": [1, 4],
    "Winter Wyvern": [4, 5],
    "Wraith King": [1, 3],
    "Zeus": [2, 4, 5],
    "Largo": [3],
}

name_to_id = {}
id_to_name = {}

# Загрузка героев (один раз)
@st.cache_data
def load_heroes():
    url = "https://api.opendota.com/api/heroes"
    resp = requests.get(url)
    if resp.status_code != 200:
        st.error("Ошибка загрузки героев")
        st.stop()
    heroes = resp.json()
    global name_to_id, id_to_name
    name_to_id = {h['localized_name']: h['id'] for h in heroes}
    id_to_name = {h['id']: h['localized_name'] for h in heroes}
    return len(heroes)
  # Функция matchup с обработкой ошибок
@st.cache_data(ttl=3600)
def get_matchups_from_opendota(hero_id):
    url = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 429:
            st.warning("Лимит запросов OpenDota — подожди 1–2 минуты")
            return {}
        if resp.status_code != 200:
            return {}
        data = resp.json()
        matchups = {}
        for m in data:
            opp_id = m['hero_id']
            games = m['games_played']
            if games > 1:  # уменьшили порог
                winrate = (m['wins'] / games) * 100
                matchups[opp_id] = {'winrate': winrate, 'games': games}
        return matchups
    except:
        return {}

# Рекомендации (твоя функция)
def recommend_heroes(my_role, enemies_names, top_k=7, mode='average'):
    if not (1 <= my_role <= 5):
        return ["Ошибка: роль 1–5"] * top_k

    if not enemies_names:
        return ["Укажите хотя бы 1–2 врага"] * top_k

    all_matchups = defaultdict(list)
    valid_enemies = 0

    for enemy_name in enemies_names[:5]:
        enemy_id = name_to_id.get(enemy_name)
        if not enemy_id:
            continue

        matchups = get_matchups_from_opendota(enemy_id)
        if matchups:
            valid_enemies += 1
            for my_hero_id, data in matchups.items():
                all_matchups[my_hero_id].append(data['winrate'])

    if valid_enemies == 0:
        return ["Нет данных по врагам — попробуй других или подожди 5 минут"] * top_k

    scores = {}
    for hero_id, winrates in all_matchups.items():
        if len(winrates) > 0:
            if mode == 'min':
                avg_winrate = min(winrates)
            else:
                avg_winrate = sum(winrates) / len(winrates)
            advantage = 50 - avg_winrate  # правильная логика!
            scores[hero_id] = advantage

    forbidden_ids = set(name_to_id.get(e) for e in enemies_names if e in name_to_id)

    candidates = []
    for hero_id, adv in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if hero_id in forbidden_ids:
            continue
        hero_name = id_to_name.get(hero_id)
        if hero_name and hero_name in hero_roles and my_role in hero_roles[hero_name]:
            candidates.append((hero_name, adv))

    recommended = []
    for name, adv in candidates[:top_k]:
        sign = '+' if adv >= 0 else ''
        recommended.append(f"{name} ({sign}{adv:.2f}%)")

    while len(recommended) < top_k:
        recommended.append("(герой не найден)")

    return recommended

# ==========================================
# САЙТ
# ==========================================

st.set_page_config(page_title="Dota 2 Рекомендатор", layout="wide")

st.title("Dota 2 Рекомендатор героев — патч 7.40")
st.markdown("Выбери свою роль и укажи врагов — получи топ-7 пиков для победы!")

load_heroes()

role = st.selectbox(
    "Твоя роль",
    ["Carry", "Mid", "Offlane", "Soft Support", "Hard Support"],
    index=0
)
role_num = {"Carry": 1, "Mid": 2, "Offlane": 3, "Soft Support": 4, "Hard Support": 5}[role]

enemies_input = st.text_input(
    "Враги (через запятую, 1–5 шт.)",
    placeholder="Medusa, Storm Spirit, Mars",
    value="Medusa, Storm Spirit, Mars"
)

if st.button("Получить рекомендации", type="primary"):
    enemies = [e.strip() for e in enemies_input.split(',') if e.strip()]
    
    if not enemies:
        st.error("Укажи хотя бы одного врага")
    else:
        with st.spinner("Загружаем данные OpenDota..."):
            recs = recommend_heroes(role_num, enemies)
        
        st.success("Рекомендованные герои:")
        for i, rec in enumerate(recs, 1):
            st.markdown(f"{i}. {rec}")

st.markdown("---")
st.caption("Данные: OpenDota API | Проект для школы")
