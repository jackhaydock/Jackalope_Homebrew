import math
import json
import glob
import copy

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

def calculate_ac(cr, formula="scale_unarmored"):
    if formula == "scale_unarmored":
        return 9 + get_prof_bonus(cr)
    elif formula == "scale_light":
        return 11 + get_prof_bonus(cr)
    elif formula == "scale_medium":
        return 13 + get_prof_bonus(cr)
    elif formula == "scale_heavy":
        return 15 + get_prof_bonus(cr)
    else:
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
    else:
        raise Exception(f"Unrecognised HP formula: {formula}")

def create_statblock_at_cr(base, meta, cr):
    output = copy.deepcopy(base)

    # Name, CR, AC and HP
    output["name"] += f" (CR{cr})"
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
            output[skill] = scale_stat(base[skill], cr, prof=True)

        if "perception" in base["skill"]:
            output["passive"] += get_prof_bonus

    # Traits
    for trait in meta["trait"]:
        for tier in meta["trait"][trait]:
            if cr in tier["crs"]:
                trait_data = {
                    "name": trait,
                    "entries": tier["entries"]
                }
                output["trait"].append(trait_data)

    # Actions
    for action in meta["action"]:
        for tier in meta["action"][action]:
            if cr in tier["crs"]:
                action_data = {
                    "name": action,
                    "entries": tier["entries"]
                }
                output["action"].append(action_data)

    # Bonus Actions
    for bonus in meta["bonus"]:
        for tier in meta["bonus"][bonus]:
            if cr in tier["crs"]:
                bonus_data = {
                    "name": bonus,
                    "entries": tier["entries"]
                }
                output["bonus"].append(bonus_data)

    # Reactions
    for reaction in meta["reaction"]:
        for tier in meta["reaction"][reaction]:
            if cr in tier["crs"]:
                reaction_data = {
                    "name": reaction,
                    "entries": tier["entries"]
                }
                output["reaction"].append(reaction_data)


    return output

def create_statblocks(data):
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