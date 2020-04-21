import glob
import json
import atexit
from pprint import pprint


def main():
    @atexit.register
    def goodbye():
        pprint(f"Saving results to file: {line_counts}")
        if line_counts is not None and len(line_counts) > 0:
            with open("results.json", "w") as results:
                json.dump(line_counts, results)
        print("Goodbye!")

    def divide_chunks(l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i : i + n]

    default = 0
    prompts = {
        "divider": "************************",
        "log": "- How many lines in the excerpt are logging-related? (default: 0) -- ",
        "bp": "- How many lines in the excerpt are boilerplate-y (default: 0) -- ",
    }

    py_files = glob.glob("data/**/*.py", recursive=True)
    py_files = [x for x in py_files if "test" not in x]

    line_counts = {}
    with open("results.json", "r") as results:
        try:
            line_counts = json.load(results)
        except json.decoder.JSONDecodeError:
            line_counts = {}

    for py_file in py_files:
        if py_file in line_counts and len(line_counts[py_file]) > 0:
            print("Skipping file; already have data.")
            continue
        elif py_file not in line_counts:
            line_counts[py_file] = {}

        these_lines = log_lines = bp_lines = []
        skip_file = True
        with open(py_file, "r") as source:
            # Litmus test -- let's not even prompt the user if this
            # particular file does not deal with logging at all.
            these_lines = source.readlines()
            these_lines = [x for x in these_lines if x != "\n"]
            these_lines = [x for x in these_lines if len(x) > 0]
            these_lines = [x for x in these_lines if not x.startswith("#")]

            for l in these_lines:
                if "log" in l:
                    skip_file = False
                    break

        if not skip_file:
            this_file_log_counts = {"log": 0, "bp": 0}

            for excerpt in divide_chunks(these_lines, 10):
                this_excerpt_log_counts = {"log": 0, "bp": 0}

                print(prompts["divider"])
                log_line_count = bp_line_count = None
                for i, l in enumerate(excerpt):
                    print(f"{i+1}: {l}")

                for l_type in this_excerpt_log_counts:
                    l_count = None
                    while l_count is None:
                        try:
                            l_count = input(prompts[l_type])
                            if len(l_count) == 0:
                                l_count = default
                            else:
                                l_count = int(l_count)
                        except ValueError:
                            print("Please enter a valid integer.")
                            l_count = None
                    this_excerpt_log_counts[l_type] += l_count
        else:
            print("Skipping this file; no logging lines found.")

        line_counts[py_file]["total"] = len(these_lines)
        line_counts[py_file]["log"] = len(log_lines)
        line_counts[py_file]["bp"] = len(bp_lines)
        print(f"For file {py_file}, we found: {line_counts[py_file]}")


if __name__ == "__main__":
    main()
