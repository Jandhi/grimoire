import inspect


def test(a, i: int, b: int, *args, **kwargs):
    pass


print(test.__kwdefaults__)
print(test.__annotations__.items())
print(inspect.getfullargspec(test))

inspect.getfullargspec(test)
