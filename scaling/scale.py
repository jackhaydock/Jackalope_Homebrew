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

def get_skill_mod(abilities, skill, cr, prof=True):
    pb = get_prof_bonus(cr) if prof else 0
    if skill in ["athletics"]:
        return 


def calculate_ac(cr, formula="scale_unarmored"):
    if formula == "scale_unarmored":
        return 9 + get_prof_bonus(cr)
    elif formula == "scale_light":
        return 11 + get_prof_bonus(cr)
    elif formula == "scale_medium":
        return 13 + get_prof_bonus(cr)
    elif formula == "scale_heavy":
        return 15 + get_prof_bonus(cr)
    raise Exception(f"Unrecognised AC formula: {formula}")

def calculate_hp(cr, formula="scale_default"):
    if formula == "scale_default":
        return (15*cr)+15
    elif formula == "scale_squishy":
        return (12*cr)+12
    elif formula == "scale_soldier":
        return (18*cr)+18
    elif formula == "scale_brute":
        return (20*cr)+20
    raise Exception(f"Unrecognised HP formula: {formula}")
    
def get_damage_avg(dice, faces, mod):
    return math.ceil(dice * ((faces/2)+0.5) + mod)

def get_damage_formuala(cr, formula):
    dice = math.ceil(cr/2)
    mod = get_ability_mod(16+get_scaling_mod(cr)) + cr
    if formula == "puny":
        avg = get_damage_avg(dice, 4, mod)
        return f"{{@h}}{avg} ({{@damage {dice}d4 + {mod}}})"
    elif formula == "weak":
        avg = get_damage_avg(dice, 6, mod)
        return f"{{@h}}{avg} ({{@damage {dice}d6 + {mod}}})"
    elif formula == "medium":
        avg = get_damage_avg(dice, 8, mod)
        return f"{{@h}}{avg} ({{@damage {dice}d8 + {mod}}})"
    elif formula == "strong":
        avg = get_damage_avg(dice, 10, mod+cr)
        return f"{{@h}}{avg} ({{@damage {dice}d10 + {mod+cr}}})"
    elif formula == "smalld6":
        small_dice = math.floor((cr+1)/4)
        avg = get_damage_avg(small_dice, 6, 0)
        return f"{avg} ({{@damage {small_dice}d6}})"
    raise Exception(f"Bad DMG formula: {formula}")
    
def get_hit_formula(cr, formula):
    if formula == "default":
        hit_mod = get_ability_mod(16+get_scaling_mod(cr)) + get_prof_bonus(cr)
        return f"{{@hit {hit_mod}}}"
    raise Exception(f"Unrecognised Hit Formula: {formula}")
    
def get_dc_formula(cr, formula):
    if formula == "default":
        dc = 8 + get_ability_mod(16+get_scaling_mod(cr)) + get_prof_bonus(cr)
        return f"{{@dc {dc}}}"
    raise Exception(f"Unrecognised DC Formula: {formula}")
    
def process_scaling_text(entries, cr):
    output = []
    for line in entries:
        formulas = re.findall("<[a-z,_,0-9]*>", line)
        for f in formulas:
            formula_type = f.split("_")[1].strip(">") 
            if re.search("^<hit_", f):
                sub_str = get_hit_formula(cr, formula_type)
            elif re.search("^<dmg_", f):
                sub_str = get_damage_formuala(cr, formula_type)
            elif re.search("^<dc_", f):
                sub_str = get_dc_formula(cr, formula_type)
            elif re.search("^<dist_", f):
                sub_str = str(10+5*(math.ceil(cr/2))) # TODO: temp formula, consider more consistent stuff for use elsewhere
            elif re.search("^<mod_", f):
                sub_str = str(get_prof_bonus(cr)) # TODO: add more mods
            else:
                raise Exception(f"Unrecognised inline formula: {f}")
            line = re.sub(f, sub_str, line)
        output.append(line)
    return output

def create_statblock_at_cr(base, meta, cr):
    output = copy.deepcopy(base)

    # Name, CR, AC and HP
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
                    "entries": process_scaling_text(tier["entries"], cr)
                }
                output["trait"].append(trait_data)

    # Actions
    for action in meta["action"]:
        for tier in meta["action"][action]:
            if cr in tier["crs"]:
                action_data = {
                    "name": action,
                    "entries": process_scaling_text(tier["entries"], cr)
                }
                output["action"].append(action_data)

    # Bonus Actions
    for bonus in meta["bonus"]:
        for tier in meta["bonus"][bonus]:
            if cr in tier["crs"]:
                bonus_data = {
                    "name": bonus,
                    "entries": process_scaling_text(tier["entries"], cr)
                }
                output["bonus"].append(bonus_data)

    # Reactions
    for reaction in meta["reaction"]:
        for tier in meta["reaction"][reaction]:
            if cr in tier["crs"]:
                reaction_data = {
                    "name": reaction,
                    "entries": process_scaling_text(tier["entries"], cr)
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