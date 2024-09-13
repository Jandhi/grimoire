from enum import Enum, auto


"""
The MaterialTraversalStrategy is the way we select the material node from its graph of connections given
some feature value 0.0 <= V <= 1.0

Imagine we have a node [COBBLESTONE] with the following connections for some feature.
ANDESITE < [COBBLESTONE] < COBBLED_DEEPSLATE < BLACKSTONE

LINEAR
Linear is the default strategy. Since cobblestone has only one node in the lesser direction and two in the greater
direction, we make the range the minimum of the two depths. That means our node can go one step higher, and one step
lower, giving a total range of 3.

So, for each band, the bandwidth == 1.0 / (1 + 2 * min(LR, GR))

When a gradient is created for this feature, it will have bands of EQUAL weight (which we refer to as S, or scale).

.......... <- S = 0.33
..........    . = ANDESITE
..........    : = COBBLESTONE
::::::::::    / = COBBLED_DEEPSLATE
::::::::::
:::::::::: <- S = 0.33
//////////
//////////
//////////
////////// <- S = 0.33


SCALED
Scaled is a strategy where we try to scale down the bands of materials to fit each one. Since our greater direction has
two nodes while the lesser only has one, bands for the greater materials will be smaller.

To keep the cobblestone in the center, we want the sum of the greater material's range to be the same as that of the
lesser materials. So we have:

lesser_range (LR) * lesser_scaling (LS) == greater_range (GR) * greater_scaling (GS)
-> LS == (GR * GS / LR)

the scaling of the middle band can be the average of the two scaling values. Since the sum of all bands must be 1, this
gives us:

LR * LS + GR * GS + (LS + GS) / 2 == 1
-> 2 * GR * GS + (GR * GS / LR + GS) / 2 == 1
-> GS * (2 * GR + (GR / LR + 1) / 2) == 1
-> GS == 2 / (4 * GR + GR / LR + 1)
-> GS == 2 / (1 + (4 + 1 / LR) * GR)

and it follows
LS == GS * GR / LR

With this example we have
LR = 1
GR = 2

so GS == 2 / (1 + (4 + 1) * 2) == 2 / 11
LS == 2 / 11 * 2 / 1 == 4 / 11
MS == 3 / 11

Giving us a gradient of something like this:
.......... <- LS = 4/11
..........
..........           . = ANDESITE
..........           : = COBBLESTONE
::::::::::           / = COBBLED_DEEPSLATE
::::::::::           # = BLACKSTONE
:::::::::: <- MS = 3/11
//////////
//////////
##########
########## <- GS = 2/11

If LR == 0, we instead fill half the gradient with the middle value, and set half an upper band to the middle value:
(GR + 1/2) * GS == 1/2
=> (2GR + 1) * GS == 1
=> GS == 1 / (2 * GR + 1)
and MS == GS / 2 + 1 / 2 == (GS + 1) / 2

And Vice Versa for GR == 0. And of course, if both are 0, we return the middle value all the time.

"""


class MaterialTraversalStrategy(Enum):
    LINEAR = auto()
    SCALED = auto()

    # Calculates the movements required across a material's feature graph
    # positive numbers are more of a feature, towards 1.0
    # negative numbers are less of a feature, towards 0.0
    def calculate_movements(
        self, material: "Material", feature: "MaterialFeature", value: float
    ) -> int:
        if self == MaterialTraversalStrategy.LINEAR:
            return self._calculate_movements_linear(material, feature, value)
        if self == MaterialTraversalStrategy.SCALED:
            return self._calculate_movements_scaled(material, feature, value)
        raise ValueError("Unexpected value")

    def _calculate_movements_linear(
        self, material: "Material", feature: "MaterialFeature", value: float
    ) -> int:
        lesser_range, greater_range = material.get_range(feature)
        smaller_range = min(lesser_range, greater_range)

        if smaller_range == 0:
            return 0

        # We clamp the top to avoid overflow
        if value == 1.0:
            value = 0.99

        band_width = 1.0 / (1 + 2 * smaller_range)
        index = int(value / band_width) - smaller_range

        return index

    def _calculate_movements_scaled(
        self, material: "Material", feature: "MaterialFeature", value: float
    ) -> int:
        lesser_range, greater_range = material.get_range(feature)

        if lesser_range == 0 and greater_range == 0:
            return 0

        if lesser_range == 0:
            if 0 <= value <= 0.5:
                return 0

            half_band_width = 1.0 / (1 / 2 + greater_range)

            index = int(((value - 0.5) / half_band_width + 1.0) / 2)
            return index

        if greater_range == 0:
            if value >= 0.5:
                return 0

            half_band_width = 1.0 / (1 / 2 + lesser_range)

            index = int(((value) / half_band_width + 1.0) / 2)
            return index

        greater_scaling = 2 / ((4 + (1 / lesser_range)) * greater_range + 1)
        lesser_scaling = greater_scaling * greater_range / lesser_range

        if value < lesser_scaling * lesser_range:
            return -lesser_range + int(value / lesser_scaling)
        elif value > 1 - greater_range * greater_scaling:
            return 1 + int(
                (value - (1 - greater_range * greater_scaling)) / greater_scaling
            )
        else:
            return 0
