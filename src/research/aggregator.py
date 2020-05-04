import glob
import json
import atexit
import csv


def main():
    @atexit.register
    def goodbye():
        print("Goodbye!")

    prompts = {
        "divider": "************************",
        "filechoice": "Which file would you like to analyze? ",
        "sourcetype": "Is this project open or closed source? ",
    }

    input_files = glob.glob("stats/**/*.json")

    print(prompts["divider"])
    print("Available files:")
    for i, fn in enumerate(input_files):
        print(f"[{i}] {fn}")
    print(prompts["divider"])
    f_index = None
    while f_index is None:
        try:
            f_index = int(input(prompts["filechoice"]))
        except ValueError:
            print("Please enter a valid integer.")
            f_index = None

    stat_filename = input_files[f_index]

    valid_source_types = ["open", "closed"]
    source_type = None
    while source_type is None:
        source_type = input(prompts["sourcetype"])
        if source_type not in valid_source_types:
            print(f"Please enter one of: {', '.join(valid_source_types)}")
            source_type = None

    results = []
    with open(stat_filename, "r") as stat_fp:
        line_counts = json.load(stat_fp)

    # Each line in results should look like:
    # [filename, open/closed, lloc, llloc, bplloc]

    for py_filename, raw_stats in line_counts.items():
        lloc = raw_stats["lloc"]
        llloc = raw_stats["llloc"]
        bplloc = raw_stats["bplloc"]
        this_line = [py_filename, source_type, lloc, llloc, bplloc]
        results.append(this_line)

    with open("aggregated.csv", "a") as agg_file:
        writer = csv.writer(agg_file)
        for l in results:
            writer.writerow(l)


if __name__ == "__main__":
    main()
