BITNOISE1 = 0x85297a4d
BITNOISE2 = 0x68e31da4
BITNOISE3 = 0x1859c4e9

# hashes together two numbers
def munge(a : int, b : int) -> int:
    noise = b
    noise = noise * BITNOISE1
    noise = noise + a
    noise = noise ^ (noise >> 8)
    noise = noise + BITNOISE2
    noise = noise ^ (noise << 8)
    noise = noise * BITNOISE3
    noise = noise ^ (noise >> 8)
    return noise