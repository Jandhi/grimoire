from .asset import Asset, AssetMeta


def link_assets():
    for AssetType in Asset.types:
        for obj in AssetType.all():
            link(obj)


# This allows for fields that are annotated with Asset types that are filled with string types on loading jsons to be instead
# swapped out for the actual Asset object.
def link(asset: Asset):
    for field_name, field_type in asset.get_annotations().items():
        if isinstance(field_type, AssetMeta) and isinstance(
            getattr(asset, field_name), str
        ):
            string_ref = getattr(asset, field_name)
            setattr(asset, field_name, field_type.find(string_ref))
        elif (
            field_type == "list"
            and hasattr(field_type, "__args__")
            and isinstance(field_type.__args__[0], AssetMeta)
        ):
            new_list = [
                field_type.__args__[0].find(string_ref)  # TODO: No attribute `find()`
                for string_ref in getattr(asset, field_name)
                if isinstance(string_ref, str)
            ]
            setattr(asset, field_name, new_list)
