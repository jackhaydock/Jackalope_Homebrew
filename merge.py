import json
import glob
import time
import pathlib
from datetime import datetime

def build_json(files):
    output = {}
    for f in files:
        # Get time file was last modifed, to be used as version
        file_modified_time = pathlib.Path(f).stat().st_mtime
        version = datetime.utcfromtimestamp(file_modified_time).strftime('%Y.%m.%d.%H.%M')

        # Build merged json from all given source jsons, extending rather than replacing where needed
        with open(f, 'r', encoding="ascii", errors="replace") as infile:
            data = json.load(infile)
            for k in data.keys():
                if k in output.keys():
                    if k == "$schema":
                        continue
                    elif k == "_meta":
                        for source in data[k]["sources"]:
                            source["version"] = version
                        output[k]["sources"].extend(data[k]["sources"])
                    else:
                        output[k].extend(data[k])
                else:
                    data["_meta"]["sources"][0]["version"] = version
                    output[k] = data[k]
                    
    output["_meta"]["dateLastModified"] = time.time()
    return output

def write_to_file(filename, data):
    with open(filename, 'w') as output_file:
        json.dump(data, output_file, indent=4)

# Get file lists
main_files = glob.glob("source_jsons/main/*.json")
extra_files = glob.glob("source_jsons/extra/*.json")
legacy_files = glob.glob("source_jsons/legacy/*.json")
all_files = main_files + extra_files + legacy_files

# Get data and write
print("-Extra")
write_to_file("merged_jsons/jackalope_extra.json", build_json(extra_files))
print("-Legacy")
write_to_file("merged_jsons/jackalope_legacy.json", build_json(legacy_files))
print("-Main")
write_to_file("merged_jsons/jackalope_main.json", build_json(main_files))
print("-All")
write_to_file("merged_jsons/jackalope_all.json", build_json(all_files))
print("Complete")