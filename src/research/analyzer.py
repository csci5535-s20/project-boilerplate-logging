import glob
import json
import atexit
from pprint import pprint


def main():
    @atexit.register
    def goodbye():
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

    input_files = ["all"] + glob.glob("stats/*.json")
    print(prompts["divider"])
    print("Available files:")
    for i, fn in enumerate(input_files):
        print(f"[{i}] {fn}")
    print(prompts["divider"])
    f_index = None
    while f_index is None:
        try:
            f_index = int(input("Which file would you like to analyze? "))
        except ValueError:
            print("Please enter a valid integer.")
            f_index = None

    stat_file = input_files[f_index]
    line_counts = {}
    with open(stat_file, "r") as stat_fp:
        try:
            line_counts = json.load(stat_fp)
        except json.decoder.JSONDecodeError:
            line_counts = {}

    for py_file, raw_stats in line_counts.items():
        raw_stats["bplloc"] = 0
        raw_stats["llloc"] = 0
        raw_stats["bppoc"] = 0.0
        raw_stats["bpgr"] = 0.0

        these_lines = []
        skip_file = True
        with open(py_file, "r") as source:
            # Litmus test -- let's not even prompt the user if this
            # particular file does not deal with logging at all.
            these_lines = source.readlines()
            these_lines = [x for x in these_lines if x != "\n"]
            these_lines = [x for x in these_lines if len(x) > 0]
            these_lines = [x for x in these_lines if not x.strip().startswith("#")]

            for l in these_lines:
                if "log" in l:
                    skip_file = False
                    break

        if not skip_file:
            print(f"Now working on: {py_file}")
            this_file_log_counts = {"log": 0, "bp": 0}

            in_comment = False
            these_real_lines = []
            for l in these_lines:
                if l.strip() == '"""':
                    in_comment = not in_comment
                    continue

                if not in_comment:
                    these_real_lines.append(l)
            these_lines = these_real_lines

            # List of lists
            excerpts = []

            tracked_indices = []
            for l in these_lines:
                skip_this_index = False
                if (" log" in l or ".log" in l) and ("import" not in l):
                    indx = these_lines.index(l)
                    for i in tracked_indices:
                        if i - 5 <= indx <= i + 5:
                            # Skip this line; we see it in another window.
                            skip_this_index = True
                            break
                    if skip_this_index:
                        continue
                    tracked_indices.append(indx)
                    excerpt = list(these_lines[(indx - 5) : (indx + 5)])
                    if len(excerpt) > 0:
                        excerpts.append(excerpt)

            print(f"Found {len(excerpts)} excerpts to analyze.")

            for excerpt in excerpts:

                print(prompts["divider"])
                for i, l in enumerate(excerpt):
                    clean_l = l if not l.endswith("\n") else l[:-1]
                    print(f"{i+1}: {clean_l}")

                for l_type in ["log", "bp"]:
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
                    this_file_log_counts[l_type] += l_count

            raw_stats["bplloc"] = this_file_log_counts["bp"]
            raw_stats["llloc"] = this_file_log_counts["log"]
            raw_stats["bppoc"] = (
                0
                if this_file_log_counts["bp"] == 0
                else (
                    (this_file_log_counts["log"] - this_file_log_counts["bp"])
                    / this_file_log_counts["log"]
                )
                * 100
            )
            raw_stats["bpgr"] = (raw_stats["lloc"] - raw_stats["bplloc"]) / raw_stats["lloc"]
        else:
            print("Skipping this file; no logging lines found.")

        print(f"For file {py_file}, we found: {line_counts[py_file]}")

    with open(stat_file, "w") as stat_fp:
        json.dump(line_counts, stat_fp, indent=4)


if __name__ == "__main__":
    main()
