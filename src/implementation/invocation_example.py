import boilerplate as bp


@bp.log
def add(x, y):
    return x + y


@bp.log("inputs")
def subtract(x, y):
    return x - y


@bp.log("outputs")
def multiply(x, y):
    return x * y


add(1, 1)
subtract(2, 1)
multiply(4, 5)
