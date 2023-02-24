from data.asset import Asset, asset_defaults

@asset_defaults()
class Industry(Asset):
    buildings : str

class PrimaryIndustry(Industry):
    req_biome_tags : list[str]

class SecondaryIndustry(Industry):
    req_industries : list[str]

def find_primary_industries(tags : list[str]):
    eligibile_primary_industries = []
    for industry in PrimaryIndustry.all():
        industry : PrimaryIndustry
                
        if any((tag not in tags for tag in industry.req_biome_tags)):
            continue
        eligibile_primary_industries.append(industry)
    return eligibile_primary_industries

def find_secondary_industries(industries : list[str]):
    eligible_secondary_industries = []
    for industry in SecondaryIndustry.all():
        industry : SecondaryIndustry

        if any((primary not in industries for primary in industry.req_industries)):
            continue
        eligible_secondary_industries.append(industry)
    return eligible_secondary_industries