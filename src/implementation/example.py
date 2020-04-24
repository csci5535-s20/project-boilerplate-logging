import boilerplate as bp

import utility


@bp.log("outputs")
def test1(x, y, operator="+"):
    return x + y


class TestClass:
    @bp.log
    def __init__(self, x, y, operator):
        self.x = x
        self.y = y
        self.op = operator

    @bp.log
    def run(self):
        return self.x + self.y

    @staticmethod
    @bp.log("inputs")
    def statik(x, y):
        return x + y

    @classmethod
    @bp.log("outputs")
    def klass(cls):
        return "test_output"

    @bp.log
    def calls_other_module(self):
        return utility.utility_function_one("te", "st", separator="/")


def main():
    x = 1
    y = 2
    operator = "+"

    test1(x, y, operator)

    test = TestClass(x, y, operator)
    test.run()
    test.statik(x, y)
    test.klass()

    test.calls_other_module()

    utility.utility_function_one("te", "st", separator="/")
    try:
        utility.raises_exception()
    except Exception:
        pass


if __name__ == "__main__":
    main()
