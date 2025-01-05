from grimoire.core.styling.materials.material import Material, MaterialFeature
from grimoire.core.styling.materials.traversal import MaterialTraversalStrategy

material_a = Material()
material_b = Material()
material_c = Material()
material_d = Material()

material_a.connections = {MaterialFeature.SHADE: (None, material_b)}
material_b.connections = {MaterialFeature.SHADE: (material_a, material_c)}
material_c.connections = {MaterialFeature.SHADE: (material_b, material_d)}
material_d.connections = {MaterialFeature.SHADE: (material_c, None)}

material_a.feature_ranges = {MaterialFeature.SHADE: (0, 3)}
material_b.feature_ranges = {MaterialFeature.SHADE: (1, 2)}
material_c.feature_ranges = {MaterialFeature.SHADE: (2, 1)}
material_d.feature_ranges = {MaterialFeature.SHADE: (3, 0)}

symbols = [".", ":", "/", "#"]

# LINEAR
index = MaterialTraversalStrategy.LINEAR.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.3
)
assert index == -1
index = MaterialTraversalStrategy.LINEAR.calculate_movements(
    material_b, MaterialFeature.SHADE, 1.0
)
assert index == 1
index = MaterialTraversalStrategy.LINEAR.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.65
)
assert index == 0

print("LINEAR GRADIENT")
lines = 11
for i in range(lines):
    val = i / lines
    index = MaterialTraversalStrategy.LINEAR.calculate_movements(
        material_b, MaterialFeature.SHADE, val
    )
    print(symbols[index + 1] * 10)
print()

# SCALING
index = MaterialTraversalStrategy.SCALED.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.3
)
assert index == -1

index = MaterialTraversalStrategy.SCALED.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.5
)
assert index == 0
index = MaterialTraversalStrategy.SCALED.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.7
)
assert index == 1
index = MaterialTraversalStrategy.SCALED.calculate_movements(
    material_b, MaterialFeature.SHADE, 0.8
)
assert index == 2

print("SCALED GRADIENT")
lines = 11
for i in range(lines):
    val = i / lines
    index = MaterialTraversalStrategy.SCALED.calculate_movements(
        material_b, MaterialFeature.SHADE, val
    )
    print(symbols[index + 1] * 10)
print()
