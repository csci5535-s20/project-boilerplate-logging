import boilerplate as bp


@bp.trace
def add(x, y):
    return x + y


@bp.trace
def subtract(x, y):
    return x - y


@bp.trace
def multiply(x, y):
    return x * y


add(1, 1)
subtract(2, 1)
bp.flush()

bp.register_uncaught_exception_handler()
multiply(4, 5)
raise Exception("trigger flush of boilerplate logs")
