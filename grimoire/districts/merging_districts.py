from ..core.maps import Map
from ..districts.district import District, SuperDistrict
from ..districts.district_analyze import district_analyze, get_candidate_score

RURAL_SIZE_RATIO = 3  # NOTE: not currently used, we expect rural districts to be this times larger in area than urban ones


# Merges districts until we have a target number reached
def merge_down(
    districts: list[District],
    district_map: list[list[District]],
    target_number: int,
    main_map: Map,
) -> None:
    identities: dict[District, District] = {
        district: district for district in districts
    }  # tracks whether a districts is truly itself
    district_count: int = len(districts)

    ignore: set[District] = set()

    while district_count > target_number:
        child: District = find_smallest_adjusted_district(districts, ignore)

        if child is None:
            break

        neighbours: list[District] = child.get_adjacent_districts()

        parent: District = get_best_merge_candidate(child, neighbours)

        if parent is None:
            ignore.add(child)

            if child.area < 10:  # remove garbage districts
                districts.remove(child)
                district_count -= 1
                identities[child] = None

            continue

        merge(parent, child, districts, identities)
        district_analyze(
            parent, main_map
        )  # NOTE: could optimize by moving the calcucations in merge and using the district numbers instead of recalculating
        district_count -= 1

    fix_map_and_edges(district_map, districts, identities)


def find_smallest_adjusted_district(
    districts: list[District], ignore: set[District]
) -> District | None:
    smallest: District | None = None
    area: int | None = None

    for district in districts:
        if district in ignore:
            continue

        if area is None or district.area < area:
            smallest = district
            area = district.area

    return smallest


def get_best_merge_candidate(
    district: District, options: list[District]
) -> District | None:
    best: District | None = None
    best_score: float = (
        0.33  # NOTE: minimum score to beat else it won't be merged with any neighbour, to test this value
    )
    candidate_scores = {}

    for option in options:
        if (
            district.is_border != option.is_border
        ):  # don't merge different types of districts!
            continue

        score: float = get_candidate_score(district, option)
        candidate_scores[option] = score
        if score > best_score:
            best = option
            best_score = score

    # output: str = f"\tConsidering options for {district}: "
    # for candidate, score in candidate_scores.items():
    #     output += f"({candidate}: {score}) "
    # print(output)

    return best


# merges child districts into parent
# NOTE: this will create outdated edges (between parent and child).
# Edges should be scanned for again after the merging process.
def merge(
    parent: SuperDistrict,
    child: District,
    districts: list[District],
    identities: dict[District, District],
) -> None:
    # print(f"\tMerging {child} into {parent}")

    if isinstance(child, SuperDistrict):
        for district in child.districts:
            parent.districts.append(district)
    else:
        parent.districts.append(child)

    districts.remove(child)
    identities[child] = parent

    parent.area += child.area
    parent.edges |= child.edges  # set addition

    parent.points |= child.points
    parent.points_2d |= child.points_2d

    # merge child's neighborus to parent
    for district, adjacency_count in child.adjacency.items():
        if district == parent:
            continue

        if district not in parent.adjacency:
            parent.adjacency[district] = 0

        parent.adjacency[district] += adjacency_count
        parent.adjacencies_total += adjacency_count

    parent.adjacency.pop(child)

    # switch child for parent in other districts
    for district in districts:
        if district == parent:
            continue

        if child in district.adjacency:
            if parent not in district.adjacency:
                district.adjacency[parent] = 0

            district.adjacency[parent] += district.adjacency[child]
            district.adjacency.pop(child)

    # add alias tracking for districts map
    for alias in list(identities.keys()):
        if identities[alias] == child:
            identities[alias] = parent


def fix_map_and_edges(
    district_map: list[list[District]],
    districts: list[District],  # FIXME: Unused parameter
    identities: dict[District, District],
) -> None:
    # Fixes map
    for item in district_map:
        for z in range(len(district_map[0])):
            district: District = item[z]

            if district != None:
                item[z] = identities[district]
