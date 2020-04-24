import boilerplate as bp


@bp.log
def utility_function_one(s1, s2, separator=":"):
    return s1 + separator + s2


@bp.log
def raises_exception():
    raise Exception("this is a test exception")
