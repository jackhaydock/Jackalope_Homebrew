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
    ability_mod = get_ability_mod(16+get_scaling_mod(cr))
    num_formulas = {
        "halfcrup": math.ceil(cr/2), # CR/2 rounded up, this is the standard for most attacks
        "halfcrdown:": math.floor(cr/2), # CR/2 rounded down, starts with 1 die at CR 2/3 then +1 every 2 CRs
        "4s1": math.floor((cr+1)/4)+1, # Scale every 4 crs starting with 1 die at CR 1
        "4s3": math.floor((cr+1)/4), # Above but starting with 1 die at CR 3, good for riders that start later
    }   
    attack_formulas = {
        "puny": (num_formulas["halfcrup"], 4, ability_mod+cr),
        "weak": (num_formulas["halfcrup"], 6, ability_mod+cr),
        "medium": (num_formulas["halfcrup"], 8, ability_mod+cr),
        "strong": (num_formulas["halfcrup"], 10, ability_mod+(cr)),
        "epic": (num_formulas["halfcrup"], 12, ability_mod+(cr))
    }

    if formula == "minion":
        dmg_by_cr = get_prof_bonus(cr) + math.ceil(cr/10)
        dmg = dmg_by_cr if dmg_by_cr <= cr else cr
        return f"{{@h}} {dmg}"
    elif formula in attack_formulas.keys():
        num, face, mod = attack_formulas[formula]
        return f"{{@h}} {get_damage_str(num, face, mod)}"
    else:
        # This assumes the dmg is not an attack and does not include the '{@h}'
        form_num, form_face, *form_mods  = formula.split("_")
        num = num_formulas[form_num]
        face = int(form_face.strip("ds"))
        mod = form_mods[0] if form_mods else 0
        return get_damage_str(num, face, mod)
    
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
        "pb2": get_prof_bonus(cr)*2,
        "pb3": get_prof_bonus(cr)*3,
        "pb5": get_prof_bonus(cr)*5,
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
        # TODO: Current implementation cannot handle nested objects and lists in entries, it just copies them wholesale
        if isinstance(line, str):
            formulas = re.findall("<[a-z,_,0-9]*>", line)
            for f in formulas:
                if f == "<name>":
                    sub_str = name.lower()
                else:
                    formula_type = f.split("_", 1)[1].strip(">")
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

    # Add Scaled tag to allow filtering all but one cr for each
    if cr != meta["primary_cr"]:
        output["type"]["tags"].append("scaled")
    
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
    print(f"-{name}")
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

meta_files = glob.glob("scaling\\source\\_meta_*.json")
for file in meta_files:
    type = file.replace("scaling\\source\\_meta_", "").replace(".json", "")
    src_files = glob.glob(f"scaling\\source\{type}_*.json")

    output_data = read_from_file(file)
    for f in src_files:
        input = read_from_file(f)
        output_data["monster"].extend(create_statblocks(input))

    dest_file = f"source_jsons/main/scaling_{type}.json"
    write_to_file(dest_file, output_data)
print("Complete")