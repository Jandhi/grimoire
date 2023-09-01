import sys
sys.path[0] = sys.path[0].removesuffix('\\industries')

import industries.biome_tags as bt

all_biomes = {
    'plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'sunflower_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'snowy_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'meadow' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'tundra' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'snowy_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE), 
    'ice_spikes' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE), 
    'snowy_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'grove' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'snowy_slopes' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'jagged_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_SMALL_BODY),
    'snowy_beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL),
    'frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'old_growth_pine_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'desert' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'mangrove_swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'eroded_badlands' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'wooded_badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'warm_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'deep_lukewarm_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'deep_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'cold_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'deep_cold_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'deep_frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'frozen_river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_SMALL_BODY),
    'beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    'snowy_beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL),
    'stony_shore' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    'forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'dark_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'old_growth_birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'old_growth_pine_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'snowy_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'wooded_badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'grove' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_hills' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_savanna' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'snowy_slopes' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'jagged_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'stony_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'stony_shore' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL),
    'jungle' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'sparse_jungle' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'bamboo_jungle' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'savanna' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY), 
    'savanna_plateau' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY),
    'windswept_savanna' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY),
    'old_growth_pine_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'old_growth_birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'desert' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    'forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'meadow' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'mushroom_fields' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL)
}

plains = {
    'plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'sunflower_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'snowy_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'meadow' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'tundra' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE)
}

snowy = {
    'snowy_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE), 
    'ice_spikes' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE), 
    'snowy_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'grove' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'snowy_slopes' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'jagged_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_SMALL_BODY),
    'snowy_beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL),
    'frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY)
}

cold = {
    'old_growth_pine_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    **snowy
}

# unique style
desert = {
    'desert' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE)
}

swamp = {
    'swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'mangrove_swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY)
}

badlands = {
    'badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'eroded_badlands' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'wooded_badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE)
}

ocean = {
    'warm_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'deep_lukewarm_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'deep_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_LARGE_BODY),
    'cold_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'deep_cold_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY),
    'deep_frozen_ocean' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_LARGE_BODY)
}

aquatic = {
    'river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'frozen_river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_SMALL_BODY),
    **ocean
}

shore = {
    'beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    'snowy_beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL),
    'stony_shore' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    **ocean
}

# should consider foresty things
forest = {
    'forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'dark_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'old_growth_birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'old_growth_pine_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'snowy_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'wooded_badlands' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'grove' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE)
}

# we should add more rocks
rocky = {    
    'windswept_hills' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'windswept_savanna' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'snowy_slopes' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'frozen_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'jagged_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'stony_peaks' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'stony_shore' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_LOW, bt.ACQUATIC_COASTAL)
}

# by wood
oak = {
    'forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'meadow' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'river' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    'mushroom_fields' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL),
    **badlands
 }

birch = {
    'flower_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'old_growth_birch_forest' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE),
    'desert' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'beach' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_COASTAL)
}

spruce = {
    'old_growth_pine_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'old_growth_spruce_taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'taiga' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_gravelly_hills' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    'windswept_forest' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_LOW, bt.ACQUATIC_NONE),
    **snowy
}

dark_oak = {
    'swamp' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_SMALL_BODY),
    **badlands
}

acacia = {
    'savanna' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY), 
    'savanna_plateau' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY),
    'windswept_savanna' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY),
    **badlands
 }

jungle = {
    'jungle' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'sparse_jungle' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE),
    'bamboo_jungle' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_NONE)
}

common_animal_spawners = {}
for biome in all_biomes:
    if biome in desert:
        continue
    if biome in badlands:
        continue
    if biome in shore:
        continue
    if biome in snowy:
        continue
    if biome in aquatic:
        continue
    if biome == "mushroom_fields":
        continue
    common_animal_spawners.update( {biome : all_biomes[biome]} )

horse_spawners = {
    'plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'sunflower_plains' : (bt.ROUGHNESS_LOW, bt.TEMPERATURE_MID, bt.ACQUATIC_NONE), 
    'savanna' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY), 
    'savanna_plateau' : (bt.ROUGHNESS_MID, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY),
    'windswept_savanna' : (bt.ROUGHNESS_HIGH, bt.TEMPERATURE_HIGH, bt.ACQUATIC_SMALL_BODY)
}

tag_map = {
    "all_biomes" : all_biomes,
    "plains" : plains,
    "snowy" : snowy,
    "cold" : cold,
    "desert" : desert,
    "swamp" : swamp,
    "badlands" : badlands,
    "ocean" : ocean,
    "aquatic" : aquatic,
    "shore" : shore,
    "forest" : forest,
    "rocky" : rocky,
    "oak" : oak,
    "birch" : birch,
    "spruce" : spruce,
    "dark_oak" : dark_oak,
    "acacia" : acacia,
    "jungle" : jungle,
    "horse_spawners" : horse_spawners,
    "common_animal_spawners" : common_animal_spawners
}

if __name__ == "__main__":
    print(all_biomes)