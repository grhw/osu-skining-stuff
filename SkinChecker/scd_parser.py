def scd_parse(tags_categories,files):
    final = {
        "misc": {"misc":[]}
    }
    used_tags = []
    for category in tags_categories.keys():
        tags = tags_categories[category]
        category_files = {}
        for tag in tags:
            category_files[tag] = []
            for i in files[tag]:
                category_files[tag].append(i)
            used_tags.append(tag)
        final[category] = category_files
    for tag in files.keys():
        if tag not in used_tags:
            for file in files[tag]:
                final['misc']["misc"].append(file)

    return final

def parse(scd):
    parsed = {}
    category = "misc"
    subcategory = "misc"
    for i in scd.splitlines():
        line = i.strip()
        if line.startswith("["):
            category = line.strip("[]").strip()
            subcategory = "misc"
        elif line.startswith("#"):
            subcategory = line.replace("#","",1).strip()
        else:
            if category not in parsed.keys():
                parsed[category] = {}
            if subcategory not in parsed[category].keys():
                parsed[category][subcategory] = []
            parsed[category][subcategory].append(line)
    
    return scd_parse(parsed["TagCategories"],parsed["Files"])