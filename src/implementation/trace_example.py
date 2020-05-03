import boilerplate as bp

import utility


@bp.trace
def test1(x, y, operator="+"):
    return x + y


class TestClass:
    @bp.trace
    def __init__(self, x, y, operator):
        self.x = x
        self.y = y
        self.op = operator

    @bp.trace
    def run(self):
        return self.x + self.y

    @staticmethod
    @bp.trace
    def statik(x, y):
        return x + y

    @classmethod
    @bp.trace
    def klass(cls):
        return "test_output"

    @bp.trace
    def calls_other_module(self):
        return utility.utility_function_one("te", "st", separator="/")


def main():
    bp.register_uncaught_exception_handler()

    x = 1
    y = 2
    operator = "+"

    test1(x, y, operator)

    test = TestClass(x, y, operator)
    test.run()
    test.statik(x, y)
    test.klass()

    bp.flush()

    test.calls_other_module()

    utility.utility_function_one("boiler", "plate", separator="!")
    try:
        utility.raises_exception()
    except Exception:
        pass

    raise Exception("test")


if __name__ == "__main__":
    main()
