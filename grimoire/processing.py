#!/usr/bin/env python3
"""
processing.py

This module ###
"""

import inspect
import logging
from typing import Any, Callable, Literal

logger: logging.Logger = logging.getLogger(__name__)


def example(
    alpha, beta=None, test_return=False, **kwargs
) -> dict[Literal["help", "info", "error"], Any]:

    # initial values representing type
    a = None
    b = 1
    c = "hey"

    if not test_return:
        # Do stuff
        pass

    return {"help": a, "info": b, "error": c}


class Processor:

    action: callable

    def __init__(
        self,
        action: Callable,
        required_kwargs: dict[str, type] | None = None,
        optional_kwargs: dict[str, type] | None = None,
        return_kwargs: dict[str, type] | None = None,
    ) -> None:

        def generate_empty_kwargs(kwargs: dict[str, type]):
            raise NotImplementedError()

        action_signature: inspect.Signature = inspect.signature(action)

        required_kwargs = required_kwargs or {}
        optional_kwargs = optional_kwargs or {}
        return_kwargs = return_kwargs or {}

        if not (required_kwargs and optional_kwargs):  # if they're not both set
            # ...iterate over the parameters in the signature

            for param_name, param in action_signature.parameters.items():
                if param.default is param.empty:  # A required parameter
                    required_kwargs[param_name] = param.annotation
                else:  # An optional parameter
                    optional_kwargs[param_name] = param.annotation

        print(action_signature.parameters.keys())
        print(required_kwargs)
        print(optional_kwargs)

        if action_signature.return_annotation is inspect.Signature.empty:
            logger.warning(f"{action.__name__} was missing a return annotation.")
            try:
                empty_required_kwargs = generate_empty_kwargs(required_kwargs)
                action(**empty_required_kwargs, test_return=True)
            except TypeError as e:
                logger.error(
                    f"{action.__name__} didn't have the expected signature "
                    "(kwargs were determined incorrectly, "
                    "or there was no `test_return` argument)!"
                    f"{e}"
                    "`return_kwargs` will be set to `None`"
                )
                return_kwargs = None
        else:
            print(action_signature.return_annotation)

        print(return_kwargs)


def main() -> None:
    """This module is not intended to be executed directly."""

    # raise NotImplementedError
    p1 = Processor(example)


if __name__ == "__main__":
    main()
