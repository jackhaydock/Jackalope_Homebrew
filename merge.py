import json, glob

def build_json(files):
    output = {}
    for f in files:
        print(f)
        with open(f, 'r', encoding="ascii", errors="replace") as infile:
            data = json.load(infile)

            for k in data.keys():
                print(k)
                if k in output.keys():
                    if k == "$schema":
                        continue
                    elif k == "_meta":
                        output[k]["sources"].extend(data[k]["sources"])
                    else:
                        output[k].extend(data[k])
                else:
                    output[k] = data[k]
    return output

def write_to_file(filename, data):
    with open(filename, 'w') as output_file:
        json.dump(data, output_file, indent=4)

# Get file lists
all_files = glob.glob("source_jsons/*/*.json")
extra_files = glob.glob("source_jsons/_extra/*.json")
legacy_files = glob.glob("source_jsons/_legacy/*.json")
main_files = list(set(all_files) - set(extra_files) - set(legacy_files))

# Get data and write
write_to_file("merged_jsons/jackalope_complete.json", build_json(all_files))
write_to_file("merged_jsons/jackalope_extra.json", build_json(extra_files))
write_to_file("merged_jsons/jackalope_legacy.json", build_json(legacy_files))
write_to_file("merged_jsons/jackalope_main.json", build_json(main_files))