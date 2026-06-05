import re
from collections import defaultdict

# --- 1. ARCHITECTURAL CONFIGURATION ---
CATEGORY_MAP = {
    'cereal':      {'wheat', 'rice', 'millet', 'barley', 'oats', 'rye'},
    'new_cereal':  {'maize', 'rice', 'amaranth'},
    'livestock':   {'livestock', 'swine', 'poultry', 'camels', 'horses'}, 
    'agriculture': {'legumes', 'fruit', 'beeswax', 'medicaments', 'tomato', 'palm', 'dates', 'roots', 'nuts', 'tea', 'opium', 'rubber'},
    'fish':        {'fish', 'pelagic_fish', 'shoal_fish', 'crustaceans', 'cetaceans', 'pearls'},
    'wild_game':   {'wild_game', 'bison', 'reindeer'}, 
    'lumber':      {'lumber', 'softwood', 'hardwood'}
}

NEW_WORLD = {'north_america', 'south_america', 'america'}

PRESERVED_RARES = {
    'coffee', 'potato', 'tobacco', 'elephants', 'ivory', 'silk', 'dyes', 
    'cotton', 'wine', 'apiculture', 'olives', 'saffron', 'pepper', 
    'cloves', 'chili', 'cinnamon', 'vanilla'
}

path_map = {}
province_inventory = defaultdict(lambda: defaultdict(set))
VALIDATION_LOG = []

# --- 2. MULTI-CATEGORY HIERARCHY DISPATCHER ---
MASTER_HIERARCHIES = {
    'cereal': {
        'tropical':    {'default': ['millet'], 'conditions': [('wetlands', None, ['rice', 'millet'])]},
        'calidic':     {'default': ['millet'], 'conditions': [('wetlands', None, ['rice', 'millet'])]},
        'subtropical': {'default': ['millet'], 'conditions': [('wetlands', None, ['rice', 'millet'])]},
        'sicco':       {'default': ['barley'], 'conditions': [('flatland', 'farmland', ['wheat', 'barley']), ('hills', None, ['barley', 'millet'])]},
        'arid':        {'default': ['barley'], 'conditions': [('flatland', 'farmland', ['wheat', 'barley']), ('hills', None, ['barley', 'millet'])]},
        'xeric':       {'default': ['barley'], 'conditions': [('flatland', None, ['barley']), ('hills', None, ['barley'])]},
        'mediterranean': {'default': ['barley'], 'conditions': [('flatland', 'farmland', ['wheat', 'barley', 'oats'])]},
        'oceanic':       {'default': ['barley'], 'conditions': [('flatland', 'farmland', ['wheat', 'barley', 'oats']), (None, 'grasslands', ['oats', 'barley'])]},
        'continental':   {'default': ['rye'],    'conditions': [('flatland', 'farmland', ['wheat', 'rye', 'barley']), (None, 'grasslands', ['oats', 'rye'])]},
        'mesothermal':   {'default': ['wheat', 'barley'], 'conditions': [('wetlands', None, ['rice']), ('flatland', 'farmland', ['wheat', 'barley'])]},
        'cascadic':    {'default': ['rye'], 'conditions': [('flatland', 'farmland', ['oats', 'rye'])]},
        'hemiboreal':  {'default': ['rye'], 'conditions': [('flatland', 'farmland', ['oats', 'rye'])]},
        'maritime':    {'default': ['rye'], 'conditions': [('flatland', 'farmland', ['oats', 'rye'])]},
        'arctic':      {'default': ['rye'], 'conditions': []},
        'boreal':      {'default': ['rye'], 'conditions': []},
        'cold_arid':   {'default': ['wheat', 'barley'], 'conditions': [('flatland', 'farmland', ['wheat', 'barley', 'oats'])]},
    },
    
    'new_cereal': {
        'tropical':    {'default': ['maize'], 'conditions': [('hills', None, ['amaranth', 'maize'])]},
        'calidic':     {'default': ['maize'], 'conditions': [('hills', None, ['amaranth', 'maize'])]},
        'subtropical': {'default': ['maize'], 'conditions': [('wetlands', None, ['rice', 'maize']), ('hills', None, ['amaranth', 'maize'])]},
        'sicco':       {'default': ['amaranth'], 'conditions': [('flatland', 'farmland', ['maize', 'amaranth'])]},
        'arid':        {'default': ['amaranth'], 'conditions': [('flatland', 'farmland', ['maize', 'amaranth'])]},
        'xeric':       {'default': ['amaranth'], 'conditions': []},
        'mediterranean': {'default': ['maize'], 'conditions': [('hills', None, ['amaranth', 'maize'])]},
        'oceanic':       {'default': ['maize'], 'conditions': [('wetlands', None, ['rice', 'maize']), ('hills', None, ['amaranth'])]},
        'continental':   {'default': ['maize'], 'conditions': [('wetlands', None, ['rice', 'maize']), ('hills', None, ['amaranth'])]},
        'mesothermal':   {'default': ['maize'], 'conditions': [('wetlands', None, ['rice', 'maize']), ('hills', None, ['amaranth'])]},
        'cascadic':    {'default': ['amaranth'], 'conditions': [('wetlands', None, ['rice', 'amaranth']), ('flatland', 'farmland', ['maize', 'amaranth'])]},
        'hemiboreal':  {'default': ['amaranth'], 'conditions': [('wetlands', None, ['rice', 'amaranth'])]},
        'maritime':    {'default': ['amaranth'], 'conditions': []},
        'arctic':      {'default': ['amaranth'], 'conditions': []},
        'boreal':      {'default': ['amaranth'], 'conditions': []},
        'cold_arid':   {'default': ['maize'], 'conditions': [('wetlands', None, ['rice', 'maize']), ('hills', None, ['amaranth'])]},
    },
    
    'livestock': {
        'tropical':    {'default': ['livestock'], 'conditions': [('wetlands', None, ['swine', 'poultry']), (None, 'farmland', ['poultry', 'livestock'])]},
        'calidic':     {'default': ['livestock'], 'conditions': [(None, 'farmland', ['poultry', 'livestock'])]},
        'subtropical': {'default': ['livestock'], 'conditions': [('wetlands', None, ['swine', 'poultry']), (None, 'farmland', ['poultry', 'livestock'])]},
        'sicco':       {'default': ['camels'], 'conditions': [('flatland', 'grasslands', ['livestock', 'poultry']), (None, 'farmland', ['livestock', 'poultry'])]},
        'arid':        {'default': ['camels'], 'conditions': [('hills', None, ['camels'])]},
        'xeric':       {'default': ['camels'], 'conditions': [('hills', None, ['camels'])]},
        'mediterranean': {'default': ['livestock'], 'conditions': [('flatland', 'farmland', ['poultry', 'livestock', 'swine']), ('hills', None, ['swine', 'livestock'])]},
        'oceanic':       {'default': ['livestock'], 'conditions': [('flatland', 'farmland', ['poultry', 'livestock', 'swine']), ('wetlands', None, ['swine', 'poultry']), (None, 'woods', ['swine', 'livestock'])]},
        'continental':   {'default': ['livestock'], 'conditions': [('flatland', 'grasslands', ['livestock']), (None, 'woods', ['swine', 'livestock']), (None, 'forest', ['swine'])]},
        'mesothermal':   {'default': ['livestock'], 'conditions': [('wetlands', None, ['swine', 'poultry']), ('flatland', 'farmland', ['poultry', 'livestock'])]},
        'cascadic':    {'default': ['poultry'], 'conditions': [('hills', None, ['poultry', 'livestock']), (None, 'forest', ['swine', 'livestock'])]},
        'hemiboreal':  {'default': ['livestock'], 'conditions': [('hills', None, ['poultry', 'livestock']), (None, 'forest', ['swine', 'livestock'])]},
        'maritime':    {'default': ['livestock'], 'conditions': [('hills', None, ['poultry', 'livestock']), (None, 'farmland', ['poultry', 'livestock'])]},
        'arctic':      {'default': ['poultry'], 'conditions': [(None, 'farmland', ['livestock']), (None, 'forest', ['swine'])]},
        'boreal':      {'default': ['poultry'], 'conditions': [(None, 'farmland', ['livestock']), (None, 'forest', ['swine'])]},
        'cold_arid':   {'default': ['livestock'], 'conditions': [('flatland', 'grasslands', ['livestock', 'poultry']), (None, 'woods', ['swine', 'livestock'])]},
    },
    
    'agriculture': {
        'tropical':    {'default': ['legumes'], 'conditions': [(None, 'jungle', ['palm', 'medicaments', 'legumes']), ('wetlands', None, ['palm', 'beeswax'])]},
        'calidic':     {'default': ['legumes'], 'conditions': [(None, 'forest', ['medicaments', 'beeswax', 'fruit'])]},
        'subtropical': {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['fruit', 'legumes', 'beeswax']), ('hills', None, ['medicaments', 'fruit'])]},
        'sicco':       {'default': ['dates', 'fruit'], 'conditions': [('flatland', 'farmland', ['dates', 'legumes']), ('hills', None, ['medicaments', 'fruit'])]},
        'arid':        {'default': ['dates'], 'conditions': [('flatland', None, ['dates']), ('hills', None, ['medicaments'])]},
        'xeric':       {'default': ['dates'], 'conditions': []},
        'mediterranean': {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['tomato', 'legumes', 'beeswax', 'fruit'])]},
        'oceanic':       {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['legumes', 'beeswax', 'fruit']), ('hills', None, ['medicaments', 'fruit']), (None, 'woods', ['beeswax', 'medicaments'])]},
        'continental':   {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['legumes', 'beeswax']), (None, 'woods', ['beeswax', 'medicaments', 'fruit'])]},
        'mesothermal':   {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['tomato', 'legumes', 'beeswax']), ('wetlands', None, ['palm', 'medicaments'])]},
        'cascadic':    {'default': ['beeswax'], 'conditions': [(None, 'forest', ['medicaments', 'beeswax']), ('flatland', 'farmland', ['legumes', 'fruit'])]},
        'hemiboreal':  {'default': ['beeswax'], 'conditions': [(None, 'forest', ['medicaments', 'beeswax'])]},
        'maritime':    {'default': ['beeswax'], 'conditions': [('flatland', 'farmland', ['legumes', 'fruit'])]},
        'arctic':      {'default': ['medicaments'], 'conditions': []},
        'boreal':      {'default': ['medicaments'], 'conditions': [(None, 'forest', ['beeswax'])]},
        'cold_arid':   {'default': ['legumes'], 'conditions': [('flatland', 'farmland', ['legumes', 'beeswax', 'fruit']), ('hills', None, ['medicaments'])]},
    },
    
    'fish': {
        'tropical':    {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
        'calidic':     {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': []},
        'subtropical': {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
        'sicco':       {'default': ['fish', 'shoal_fish'], 'conditions': []},
        'arid':        {'default': ['fish', 'shoal_fish'], 'conditions': []},
        'xeric':       {'default': ['fish'], 'conditions': []},
        'mediterranean': {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
        'oceanic':       {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
        'continental':   {'default': ['fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish'])]},
        'mesothermal':   {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
        'cascadic':    {'default': ['pelagic_fish', 'fish'], 'conditions': []},
        'hemiboreal':  {'default': ['pelagic_fish', 'fish'], 'conditions': []},
        'maritime':    {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': []},
        'arctic':      {'default': ['pelagic_fish', 'fish'], 'conditions': []},
        'boreal':      {'default': ['fish'], 'conditions': []},
        'cold_arid':   {'default': ['pelagic_fish', 'fish', 'shoal_fish'], 'conditions': [('wetlands', None, ['fish', 'shoal_fish'])]},
    },
    
    'lumber': {
        'tropical':    {'default': ['softwood', 'wild_game'], 'conditions': [(None, 'jungle', ['hardwood', 'medicaments'])]},
        'calidic':     {'default': ['softwood', 'wild_game'], 'conditions': [(None, 'jungle', ['hardwood'])]},
        'subtropical': {'default': ['softwood', 'wild_game', 'beeswax'], 'conditions': [(None, 'jungle', ['hardwood', 'medicaments'])]},
        'sicco':       {'default': ['softwood', 'wild_game'], 'conditions': []},
        'arid':        {'default': ['softwood', 'wild_game'], 'conditions': []},
        'xeric':       {'default': ['softwood'], 'conditions': []},
        'mediterranean': {'default': ['softwood', 'wild_game', 'beeswax'], 'conditions': []},
        'oceanic':       {'default': ['softwood', 'beeswax', 'wild_game'], 'conditions': [(None, 'woods', ['hardwood', 'beeswax', 'wild_game']), (None, 'forest', ['hardwood', 'wild_game', 'fur'])]},
        'continental':   {'default': ['softwood', 'wild_game', 'fur'], 'conditions': [(None, 'woods', ['hardwood', 'beeswax', 'wild_game']), (None, 'forest', ['hardwood', 'fur', 'wild_game'])]},
        'mesothermal':   {'default': ['softwood', 'wild_game', 'beeswax'], 'conditions': [(None, 'jungle', ['hardwood'])]},
        'cascadic':    {'default': ['softwood', 'fur', 'wild_game'], 'conditions': []},
        'hemiboreal':  {'default': ['softwood', 'fur', 'wild_game'], 'conditions': []},
        'maritime':    {'default': ['softwood', 'fur', 'wild_game'], 'conditions': []},
        'arctic':      {'default': ['softwood', 'fur'], 'conditions': []},
        'boreal':      {'default': ['softwood', 'fur', 'wild_game'], 'conditions': []},
        'cold_arid':   {'default': ['softwood', 'wild_game', 'beeswax'], 'conditions': [(None, 'woods', ['hardwood', 'beeswax', 'wild_game'])]},
    }
}

# --- 3. PARSING ---
def parse_hierarchy_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = re.sub(r'#.*', '', f.read())
        text = text.replace('{', ' { ').replace('}', ' } ').replace('=', ' = ')
        tokens = text.split()
    
    def parse_node(index):
        node_dict = {}
        node_list = []
        is_dict = False
        while index < len(tokens):
            token = tokens[index]
            if token == '}': return (node_dict if is_dict else node_list), index + 1
            if index + 1 < len(tokens) and tokens[index + 1] == '=':
                is_dict = True
                key = token
                index += 2 
                if tokens[index] == '{':
                    value, index = parse_node(index + 1)
                    node_dict[key] = value
                else:
                    node_dict[key] = tokens[index]
                    index += 1
            else:
                node_list.append(token)
                index += 1
        return (node_dict if is_dict else node_list), index

    result, _ = parse_node(0)
    return result

def flatten_hierarchy(data, current_path=None):
    if current_path is None: current_path = []
    if isinstance(data, dict):
        for key, value in data.items():
            flatten_hierarchy(value, current_path + [key])
    elif isinstance(data, list):
        for loc in data:
            path_map[loc.lower()] = set(current_path)

# --- 4. CORE GENERALIZED LOGIC ---
def get_best_material(location, climate, topo, veg, current_material, category, is_coastal=False):
    path = path_map.get(location.lower(), set())
    is_new_world = any(c in path for c in NEW_WORLD)
    loc_hash = hash(location)
    
    # --- GLOBAL AUSTRALIA LIVESTOCK PURGE ---
    if "australia_region" in path:
        if category == 'livestock' or current_material in ['wool', 'caprids', 'llamas']:
            return 'wild_game'

    # --- PRESTIGE LIVESTOCK LOCK IN PASS ---
    if current_material in ['wool', 'caprids', 'llamas']:
        if current_material == 'wool':
            if is_new_world and "south_america" in path:
                return 'llamas'
            current_material = 'caprids'
            
        # Western India Desert Camel Override (mutates caprids before the final lock)
        if current_material == 'caprids' and "western_india_region" in path and climate in ['sicco', 'arid', 'xeric']:
            if loc_hash % 2 == 0: return 'camels'
            
        return current_material # Absolute exclusion from standard reassignment pool
            
    if current_material == 'rice':
        if is_new_world and category == 'cereal':
            category = 'new_cereal'
        elif not is_new_world and category == 'new_cereal':
            category = 'cereal'

    # --- CEREAL (Old World Only) ---
    if category == 'cereal':
        if is_new_world: return current_material
        
        # Absolute Western India Override
        if "western_india_region" in path: return 'barley'
        
        if any(region in path for region in ["indochina_region", "indonesia_region", "malaya_region", "philippines_region"]):
            if current_material == 'millet':
                return 'millet' if loc_hash % 10 == 0 else 'rice'
        
        # East Asia overrides
        if any(region in path for region in ["japan_region", "korea_region"]):
            if topo == 'wetlands' or veg == 'farmland': return 'rice'
            return 'wheat' if loc_hash % 2 == 0 else 'rye'
        if any(region in path for region in ["north_china_region", "manchuria_region"]):
            return 'wheat' if loc_hash % 2 == 0 else 'rye' 
        if any(region in path for region in ["south_china_region"]):
            if climate == 'subtropical': return 'rice'
            return 'wheat' if loc_hash % 2 == 0 else 'rice'
        if any(region in path for region in ["east_china_region", "west_china_region"]):
            if climate == 'mesothermal': return 'rice'
            return 'wheat' if loc_hash % 2 == 0 else 'millet'
            
        # India override
        if "south_asia" in path:
            choices = ['rice', 'rice', 'wheat', 'millet']
            return choices[loc_hash % 4]
            
        # Regional overrides
        if "tibet_region" in path: return 'rye'
        if "arabia_region" in path: return 'barley' if loc_hash % 2 == 0 else 'wheat'
        if any(region in path for region in ["egypt_region", "chuanxia_area", "chuannan_area", "chuandong_area"]): 
            return current_material

        # Matrix Execution
        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        if config:
            priority_list = config.get('default', [current_material])
            for cond_topo, cond_veg, crops in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = crops
                    break
                    
            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in priority_list:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return priority_list[0]
            return priority_list[0]
            
        return current_material

    # --- NEW CEREAL (New World Only) ---
    if category == 'new_cereal':
        if not is_new_world: return current_material
        
        if any(region in path for region in [
            "illinois_area", "indiana_area", "michigan_area", "wisconsin_area", 
            "superior_area", "saskatchewan_area", "florida_area", "cacaxtles_province", 
            "karankawa_province", "payeye_province", "tickanwatic_province", "waco_province", 
            "akokisa_province", "bidai_province", "louisiana_area", "oklafalaya_province", 
            "oklahannali_province", "mobile_province", "canada_region"
        ]) and topo == 'wetlands': 
            return 'rice'
            
        if "andes_region" in path:
            choices = ['amaranth', 'amaranth', 'maize']
            return choices[loc_hash % 3]
            
        if "mesoamerica_region" in path:
            choices = ['amaranth', 'maize']
            return choices[loc_hash % 2]
            
        # Matrix Execution
        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        if config:
            priority_list = config.get('default', [current_material])
            for cond_topo, cond_veg, crops in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = crops
                    break
                    
            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in priority_list:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return priority_list[0]
            return priority_list[0]
            
        return current_material

    # --- LIVESTOCK ---
    if category == 'livestock':
        if is_new_world:           
            if "andes_region" in path: return 'llamas'
            return 'poultry'
            
        if "tibet_region" in path: return 'caprids'
            
        # Dedicated Camel Injection (Only diversifies from horses and livestock)
        if current_material in ['livestock', 'horses', 'camels']:
            if any(region in path for region in [
                "maghreb_region", "arabia_region", "persia_region", "khorasan_region", 
                "xinjiang_region", "pontic_steppe_region", "mongolia_region", 
                "sahel_region", "nubia_region"
            ]):
                if climate in ['sicco', 'arid', 'xeric'] or topo == 'desert':
                    if loc_hash % 2 == 0: return 'camels'
                    
        if any(region in path for region in ["pontic_steppe_region", "central_asia_region", "tartary_region", "mongolia_region"]):
            choices = ['horses', 'livestock'] 
            return choices[loc_hash % 2]

        # Matrix Execution
        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        if config:
            priority_list = config.get('default', [current_material])
            for cond_topo, cond_veg, animals in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = animals
                    break
                    
            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in priority_list:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return priority_list[0]
            return priority_list[0]
            
        return current_material
        
    # --- NON-CEREAL AGRICULTURE (WITH INTEGRATED OPIUM & RUBBER) ---
    if category == 'agriculture':
        if "egypt_region" in path: return current_material
            
        if is_new_world and any(region in path for region in ["amazon_area", "caribbean_region", "andes_region", "mesoamerica_region", "south_america"]):
            if topo in ['flatland', 'wetlands'] or veg == 'jungle' or ("south_america" in path and loc_hash % 2 == 0):
                return 'roots'
        
        if not is_new_world and any(region in path for region in ["guinea_region", "central_african_region", "kongo_region", "melanesia_region", "polynesia_region", "micronesia_region"]):
            if climate in ['tropical', 'subtropical']:
                return 'roots'
                
        if any(region in path for region in ["great_plains_region", "east_coast_region", "texas_area", "brazil_region", "guinea_region"]):
            if veg in ['woods', 'forest', 'jungle']:
                if loc_hash % 3 == 0: 
                    return 'nuts'

        # Native Rubber Infrastructure Insertion Check
        if is_new_world and any(region in path for region in ["amazon_area", "brazil_region", "mesoamerica_region"]):
            if climate == 'tropical' and veg == 'jungle' and loc_hash % 10 == 0:
                return 'rubber'

        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        
        if config:
            priority_list = config.get('default', [current_material])
            for cond_topo, cond_veg, crops in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = crops
                    break
            
            cleaned_priority = []
            for crop in priority_list:
                if crop == 'medicaments':
                    # Asian/Near East Opium & Tea Injection Core
                    if any(region in path for region in ["india_region", "china_region", "indochina_region", "persia_region", "tibet_region", "khorasan_region", "crescent_region", "south_asia", "south_china_region", "west_china_region"]):
                        roll = loc_hash % 10
                        if roll < 2: cleaned_priority.append('tea')
                        elif roll < 5: cleaned_priority.append('opium')
                        else: cleaned_priority.append('medicaments')
                        continue
                    elif loc_hash % 3 != 0:
                        if climate in ['sicco', 'arid', 'xeric']: cleaned_priority.append('dates')
                        else: cleaned_priority.append('legumes')
                        continue

                if crop == 'tomato' and not is_new_world:
                    if 'legumes' not in cleaned_priority: cleaned_priority.append('legumes')
                    continue
                if crop == 'palm' and is_new_world and "caribbean_region" not in path:
                    if 'legumes' not in cleaned_priority: cleaned_priority.append('legumes')
                    continue
                    
                cleaned_priority.append(crop)
                
            if not cleaned_priority: cleaned_priority = ['legumes']

            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in cleaned_priority:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return cleaned_priority[0]
            return cleaned_priority[0]
            
    # --- FISH ---
    if category == 'fish':
        if current_material == 'pearls':
            return 'pearls'
            
        if any(region in path for region in ["oman_area", "bahrein_area", "fars_area", "caribbean_region", "south_yemen_area", "north_yemen_area", "hejaz_area", "northern_ethiopia_area", "japan_region", "polynesia_region", "melanesia_region", "micronesia_region"]):
            if is_coastal and loc_hash % 4 == 0: 
                return 'pearls'
                
        if any(region in path for region in ["scandinavian_region", "great_britain_region", "cascadia_area", "alaska_region", "japan_region", "east_siberia_region", "newfoundland_area", "acadia_area", "prince_edward_island_area", "maine_area", "massachusetts_area"]):
            if is_coastal and loc_hash % 5 == 0:
                return 'cetaceans'
                
        if any(region in path for region in ["maryland_area", "virginia_area", "north_carolina_area", "new_jersey_area", "scandinavian_region", "ireland_region", "great_britain_region", "northern_germany_region", "baltic_region", "indochina_region", "indonesia_region", "la_plata_region"]):
            if loc_hash % 3 == 0:
                return 'crustaceans'
                
        if any(region in path for region in ["andes_region", "guinea_region", "scandinavian_region", "russia_region"]):
            if is_coastal and loc_hash % 50 == 0:
                return 'shoal_fish'

        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        
        if config:
            priority_list = config.get('default', [current_material])
            for cond_topo, cond_veg, crops in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = crops
                    break
            
            cleaned_priority = []
            for fish_type in priority_list:
                if fish_type == 'pelagic_fish' and not is_coastal:
                    if 'fish' not in cleaned_priority: cleaned_priority.append('fish')
                    continue
                cleaned_priority.append(fish_type)
                
            if not cleaned_priority: cleaned_priority = ['fish']

            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in cleaned_priority:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return cleaned_priority[0]
            return cleaned_priority[0]
            
    # --- WILD GAME SYSTEM (BISON & REINDEER SPLIT ENGINES) ---
    if category == 'wild_game':
        # 1. Dedicated Bison Split Architecture
        if any(region in path for region in ["great_plains_region", "aridoamerica_region", "west_coast_region"]):
            spawn_chance = 35  # Standard baseline
            if veg == 'grasslands' or topo == 'flatland':
                spawn_chance = 80  # Heavily dominate open prairie
            elif veg in ['woods', 'forest']:
                spawn_chance = 45
            elif climate in ['arid', 'sicco']:
                spawn_chance = 55
                
            if (abs(loc_hash) % 100) < spawn_chance:
                return 'bison'
            return 'wild_game'
            
        # 2. Dedicated Reindeer Split Architecture
        if any(region in path for region in ["scandinavian_region", "ural_region", "north_asia", "alaska_region", "canada_region"]):
            spawn_chance = 30  # Standard baseline
            if climate in ['arctic', 'boreal']:
                spawn_chance = 85  # Deep environmental freeze domination
            elif climate == 'hemiboreal' or veg in ['forest', 'woods']:
                spawn_chance = 55
                
            if (abs(loc_hash) % 100) < spawn_chance:
                return 'reindeer'
            return 'wild_game'

        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        if config:
            priority_list = config.get('default', ['wild_game'])
            return priority_list[0]
        return 'wild_game'
            
    # --- LUMBER ---
    if category == 'lumber':
        category_rules = MASTER_HIERARCHIES.get(category, {})
        config = category_rules.get(climate)
        
        if config:
            priority_list = config.get('default', ['softwood'])
            for cond_topo, cond_veg, options in config.get('conditions', []):
                if (cond_topo is None or topo == cond_topo) and (cond_veg is None or veg == cond_veg):
                    priority_list = options
                    break
            
            cleaned_priority = []
            for wood in priority_list:
                if wood == 'lumber': wood = 'softwood'
                if wood == 'hardwood':
                    if any(region in path for region in [
                        "brazil_region", "kongo_region", "guinea_region", 
                        "indonesia_region", "indochina_region", "south_asia", 
                        "mesoamerica_region", "caribbean_region"
                    ]):
                        cleaned_priority.append('hardwood')
                    else:
                        if 'softwood' not in cleaned_priority: cleaned_priority.append('softwood')
                    continue
                cleaned_priority.append(wood)
                
            if not cleaned_priority: cleaned_priority = ['softwood']
            
            province = next((p for p in path if '_province' in p), None)
            if province:
                for item in cleaned_priority:
                    if item not in province_inventory[province][category]:
                        province_inventory[province][category].add(item)
                        return item
                return cleaned_priority[0]
            return cleaned_priority[0]
        return 'softwood' 

    return current_material

# --- 5. EXECUTION ENGINE ---
def run_reclassification(input_file, output_file):
    print("Parsing definitions...")
    geo_dict = parse_hierarchy_file('definitions_new.txt')
    flatten_hierarchy(geo_dict)
    
    print("Processing location file via bracket-buffer...")
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        bracket_level = 0
        loc_name = None
        buffer = []
        
        for line in f_in:
            if bracket_level == 0:
                loc_match = re.match(r'^\s*([a-zA-Z0-9_]+)\s*=', line)
                if loc_match:
                    loc_name = loc_match.group(1).lower()
            
            buffer.append(line)
            bracket_level += line.count('{')
            bracket_level -= line.count('}')
            
            if bracket_level == 0 and loc_name:
                block_text = "".join(buffer)
                m_match = re.search(r'raw_material\s*=\s*"?([a-zA-Z0-9_]+)"?', block_text)
                
                if m_match:
                    current_mat = m_match.group(1).lower()
                    
                    # --- ABSOLUTE PRESERVATION GUARDRAIL ---
                    if current_mat in PRESERVED_RARES:
                        f_out.write(block_text)
                        buffer = []
                        loc_name = None
                        continue
                        
                    c_match = re.search(r'climate\s*=\s*"?([a-zA-Z0-9_]+)"?', block_text)
                    t_match = re.search(r'topography\s*=\s*"?([a-zA-Z0-9_]+)"?', block_text)
                    v_match = re.search(r'vegetation\s*=\s*"?([a-zA-Z0-9_]+)"?', block_text)
                    
                    if c_match:
                        c = c_match.group(1).lower()
                        t = t_match.group(1).lower() if t_match else None
                        v = v_match.group(1).lower() if v_match else None
                        is_coastal = bool(re.search(r'natural_harbor_suitability', block_text))
                        
                        matched_category = None
                        for category_name, materials_set in CATEGORY_MAP.items():
                            if current_mat in materials_set:
                                matched_category = category_name
                                break
                        
                        # Catch prestige wool assets that aren't mapped directly in standard livestock sets
                        if current_mat in ['wool', 'caprids', 'llamas']:
                            matched_category = 'livestock'

                        if matched_category:
                            new_mat = get_best_material(loc_name, c, t, v, current_mat, matched_category, is_coastal)
                        else:
                            new_mat = current_mat
                        
                        if new_mat != current_mat:
                            block_text = re.sub(
                                r'(raw_material\s*=\s*"?)[a-zA-Z0-9_]+("?)', 
                                rf'\g<1>{new_mat}\g<2>', 
                                block_text, 
                                count=1
                            )
                            VALIDATION_LOG.append({
                                'loc': loc_name, 
                                'cat': matched_category, 
                                'old': current_mat, 
                                'new': new_mat
                            })
                
                f_out.write(block_text)
                buffer = []
                loc_name = None
                
            elif bracket_level == 0 and not loc_name:
                f_out.write("".join(buffer))
                buffer = []

    print(f"\n--- Multi-Category Validation Report ---")
    print(f"Finished reclassifying. Made {len(VALIDATION_LOG)} total changes.")
    
    category_distribution = defaultdict(int)
    for entry in VALIDATION_LOG:
        category_distribution[entry['cat']] += 1
        
    print("Changes broken down by tracking system:")
    for cat_name in CATEGORY_MAP.keys():
        print(f"  * [{cat_name.upper()}]: {category_distribution[cat_name]} swaps executed.")

if __name__ == "__main__":
    run_reclassification('base_location_templates.txt', 'reclassified_locations.txt')