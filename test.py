def func(a):
    print(a)

    return a


@func
class A:
    pass


class A:
    pass


A = func(A)

a = A()

print()
