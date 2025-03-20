import math, json, glob, copy, re

def get_ability_mod(score):
    return math.floor((score-10)/2)

def get_prof_bonus(cr):
    return math.ceil(cr/4)+1

def get_scaling_mod(cr):
    # +2 ability at CR 3 and then every 4 crs (i.e +1 to mods every other CR except PB ones)
    return (math.floor((cr+1)/4))*2

def scale_stat(base, cr, prof=False):
    pb = get_prof_bonus(cr) if prof else 0
    return base + get_scaling_mod(cr) + pb

def calculate_ac(cr, formula):
    ac_formulas = {
        "ac_unarmored": 9,
        "ac_light": 11,
        "ac_medium": 13,
        "ac_heavy": 15
    }
    try:
        return ac_formulas[formula] + get_prof_bonus(cr)
    except KeyError as ex:
        raise Exception(f"Unrecognised AC formula: {formula}")

def calculate_hp(cr, formula):
    hp_formulas = {
        "hp_minion": 7+cr,
        "hp_puny": (10*cr)+10,
        "hp_weak": (12*cr)+12,
        "hp_default": (15*cr)+15,
        "hp_strong": (18*cr)+18,
        "hp_epic": (20*cr)+20
    }
    try:
        return hp_formulas[formula]
    except KeyError as ex:
        raise Exception(f"Unrecognised HP formula: {formula}")
    
def get_damage_str(dice, faces, mod=0):
    avg = math.ceil(dice * ((faces/2)+0.5) + mod)
    mod_str = f" + {mod}" if mod != 0 else ""
    return f"{avg} ({{@damage {dice}d{faces}{mod_str}}})"

def get_damage_formuala(cr, formula):
    dice = math.ceil(cr/2)
    small_dice = math.floor((cr+1)/4)
    mod = get_ability_mod(16+get_scaling_mod(cr))
    if formula == "minion":
        dmg_by_cr = get_prof_bonus(cr) + math.ceil(cr/10)
        dmg = dmg_by_cr if dmg_by_cr <= cr else cr
        return f"{{@h}} {dmg}"
    elif formula == "puny":
        return f"{{@h}} {get_damage_str(dice, 4, mod+cr)}"
    elif formula == "weak":
        return f"{{@h}} {get_damage_str(dice, 6, mod+cr)}"
    elif formula == "medium":
        return f"{{@h}} {get_damage_str(dice, 8, mod+cr)}"
    elif formula == "strong":
        return f"{{@h}} {get_damage_str(dice, 10, mod+(2*cr))}"
    elif formula == "epic":
        return f"{{@h}} {get_damage_str(dice, 12, mod+(2*cr))}"
    elif formula == "d4s":
        return get_damage_str(small_dice, 4)
    elif formula == "d6s":
        return get_damage_str(small_dice, 6)
    elif formula == "d8s":
        return get_damage_str(small_dice, 8)
    elif formula == "d10s":
        return get_damage_str(small_dice, 10)
    raise Exception(f"Bad DMG formula: {formula}")
    
def get_hit_formula(cr, formula):
    ability = {
        "weak": 14,
        "default": 16,
        "strong": 18
    }
    try:
        hit_mod = get_ability_mod(ability[formula] + get_scaling_mod(cr)) + get_prof_bonus(cr)
        return f"{{@hit {hit_mod}}}"
    except KeyError as ex:
        raise Exception(f"Unrecognised Hit Formula: {formula}")
    
def get_dc_formula(cr, formula):
    if formula == "default":
        dc = 8 + get_ability_mod(16+get_scaling_mod(cr)) + get_prof_bonus(cr)
        return f"{{@dc {dc}}}"
    raise Exception(f"Unrecognised DC Formula: {formula}")

def get_mod_formulas(cr, formula):
    mod_formulas = {
        "pb": get_prof_bonus(cr),
        "scale1": get_scaling_mod(cr)/2,
        "scale2": get_scaling_mod(cr),
        "scale3": get_scaling_mod(cr)*1.5,
        "scale4": get_scaling_mod(cr)*2
    }
    try:
        return str(math.floor(mod_formulas[formula]))
    except KeyError as ex:
        raise Exception(f"Unrecognised Formula: {formula}")
    
def process_scaling_text(entries, cr, name):
    output = []
    for line in entries:
        formulas = re.findall("<[a-z,_,0-9]*>", line)
        for f in formulas:
            if f == "<name>":
                sub_str = name.lower()
            else:
                formula_type = f.split("_")[1].strip(">")
                if f == "<name>":
                    sub_str = name.lower()
                elif re.search("^<hit_", f):
                    sub_str = get_hit_formula(cr, formula_type)
                elif re.search("^<dmg_", f):
                    sub_str = get_damage_formuala(cr, formula_type)
                elif re.search("^<dc_", f):
                    sub_str = get_dc_formula(cr, formula_type)
                elif re.search("^<dist_", f):
                    sub_str = str(10+5*(math.ceil(cr/2))) # TODO: temp formula, consider more consistent stuff for use elsewhere
                elif re.search("^<mod_", f):
                    sub_str = get_mod_formulas(cr, formula_type)
                else:
                    raise Exception(f"Unrecognised inline formula: {f}")
            line = re.sub(f, sub_str, line)
        output.append(line)
    return output

def create_statblock_at_cr(base, meta, cr):
    output = copy.deepcopy(base)

    # Name, CR, AC and HPcd d
    output["name"] += f" (CR {cr})"
    output["cr"] = str(cr)
    output["ac"] = [
        {
            "ac": calculate_ac(cr, formula=base["ac"])
        }
    ]
    output["hp"] = {
        "special": str(calculate_hp(cr, formula=base["hp"]))
    }
    
    # Ability Scores
    for stat in ["str", "dex", "con", "int", "wis", "cha"]:
        output[stat] = scale_stat(base[stat], cr)
    
    # Saves, if any
    for save in base["save"]:
        mod = get_ability_mod(output[save]) + get_prof_bonus(cr)
        output["save"][save] = f"+{mod}"

    # Skills and Passive Perception
    output["passive"] = 10 + get_ability_mod(output["wis"])
    if "skill" in base.keys():
        for skill in base["skill"]:
            if skill in ["athletics"]:
                skill_mod = get_ability_mod(output["str"])
            elif skill in ["acrobatics", "sleight of hand", "stealth"]:
                skill_mod = get_ability_mod(output["dex"])
            elif skill in ["arcana", "history", "investigation", "nature", "religion"]:
                skill_mod = get_ability_mod(output["int"])
            elif skill in ["animal handling", "insight", "medicine", "perception", "survival"]:
                skill_mod = get_ability_mod(output["wis"])
            elif skill in ["deception", "intimidation", "performance", "persuasion"]:
                skill_mod = get_ability_mod(output["cha"])
            else:
                raise Exception(f"Unknown skill: {skill}")

            output["skill"][skill] = f"+{skill_mod + get_prof_bonus(cr)}"


        if "perception" in base["skill"]:
            output["passive"] += get_prof_bonus(cr)

    # Traits
    for trait in meta["trait"]:
        for tier in meta["trait"][trait]:
            if cr in tier["crs"]:
                trait_data = {
                    "name": trait,
                    "entries": process_scaling_text(tier["entries"], cr, base["name"])
                }
                output["trait"].append(trait_data)

    # Actions
    for action in meta["action"]:
        for tier in meta["action"][action]:
            if cr in tier["crs"]:
                action_data = {
                    "name": action,
                    "entries": process_scaling_text(tier["entries"], cr, base["name"])
                }
                output["action"].append(action_data)

    # Bonus Actions
    for bonus in meta["bonus"]:
        for tier in meta["bonus"][bonus]:
            if cr in tier["crs"]:
                bonus_data = {
                    "name": bonus,
                    "entries": process_scaling_text(tier["entries"], cr, base["name"])
                }
                output["bonus"].append(bonus_data)

    # Reactions
    for reaction in meta["reaction"]:
        for tier in meta["reaction"][reaction]:
            if cr in tier["crs"]:
                reaction_data = {
                    "name": reaction,
                    "entries": process_scaling_text(tier["entries"], cr, base["name"])
                }
                output["reaction"].append(reaction_data)


    return output

def create_statblocks(data):
    name = data["base_statblock"]["name"]
    output_list = []
    for cr in data["scaling"]["crs"]:
        output_list.append(create_statblock_at_cr(data["base_statblock"], data["scaling"], cr))
    return output_list

def read_from_file(filename):
    with open(filename, 'r', encoding="ascii", errors="replace") as infile:
        return json.load(infile)

def write_to_file(filename, data):
    with open(filename, 'w') as output_file:
        json.dump(data, output_file, indent=4)

meta_files = glob.glob("source/_meta_*.json")
for file in meta_files:
    type = file.strip("source\\_meta_").strip(".json")
    src_files = glob.glob(f"source/{type}_*.json")

    output_data = read_from_file(file)
    for f in src_files:
        input = read_from_file(f)
        output_data["monster"].extend(create_statblocks(input))

    dest_file = f"../source_jsons/main/scaling_{type}.json"
    write_to_file(dest_file, output_data)