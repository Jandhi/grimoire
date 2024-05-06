import typing
from enum import Enum
from typing import Union

from .asset import Asset, AssetMeta


def link_assets():
    for AssetType in Asset.types:
        # skip child types since they already appear in their parents
        if len(AssetType.parent_types) > 0:
            continue

        for obj in AssetType.all():
            link(obj)

    # call on link
    for AssetType in Asset.types:
        # skip child types since they already appear in their parents
        if len(AssetType.parent_types) > 0:
            continue

        for obj in AssetType.all():
            obj.on_link()


# This allows for fields that are annotated with Asset types that are filled with string types on loading jsons to be instead
# swapped out for the actual Asset object.
def link(asset: Asset):
    for field_name, field_type in asset.get_annotations().items():
        # If the type is an asset, link it
        if isinstance(field_type, AssetMeta) and isinstance(
            getattr(asset, field_name), str
        ):
            string_ref = getattr(asset, field_name)
            setattr(asset, field_name, field_type.find(string_ref))
        # If the type is a list, link the items in that list
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
        # If the type is a dict, link the items in that dict
        elif (
            field_type == "dict"
            or (hasattr(field_type, "__name__") and field_type.__name__ == "dict")
            and hasattr(field_type, "__args__")
            and isinstance(field_type.__args__[0], AssetMeta)
        ):
            new_dict = {
                field_type.__args__[0].find(
                    string_ref
                ): val  # TODO: No attribute `find()`
                for (string_ref, val) in getattr(asset, field_name).items()
            }
            setattr(asset, field_name, new_dict)
        # If the type is a union where the first type in the union is an asset, link to that asset
        elif (
            typing.get_origin(field_type) is not None
            and typing.get_origin(field_type).__name__ == "UnionType"
            and hasattr(field_type, "__args__")
            and isinstance(field_type.__args__[0], AssetMeta)
        ):
            string_ref = getattr(asset, field_name)
            setattr(asset, field_name, field_type.__args__[0].find(string_ref))
        # If the type is an enum, find the right field in that enum
        elif Enum in field_type.__mro__:
            enum_value_name = getattr(asset, field_name)
            setattr(asset, field_name, field_type[enum_value_name])
