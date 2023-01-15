BITNOISE1 = 0x85297a4d
BITNOISE2 = 0x68e31da4
BITNOISE3 = 0x1859c4e9
BITNOISE4 = 0x0c1fc20b

# hashes together a seed and a position
def hash(seed : int, pos : int) -> int:
    noise = pos
    noise = noise * BITNOISE1
    noise = noise + seed
    noise = noise ^ (noise >> 8)
    noise = noise + BITNOISE2
    noise = noise ^ (noise << 8)
    noise = noise * BITNOISE3
    noise = noise ^ (noise >> 8)
    return noise