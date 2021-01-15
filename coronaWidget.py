#!/usr/bin/env python3
import argparse, json, urllib.request

# Create the parser
my_parser = argparse.ArgumentParser()

# Add the arguments
my_parser.add_argument(
    "-c",
    "--country",
    help="Specify the country you want to display.",
    dest="country",
    required=True,
)

my_parser.add_argument(
    "-p",
    "--province",
    help="Specify the province of the coutry you want to display.",
    dest="province",
)
my_parser.add_argument(
    "-pre",
    "--prefix",
    help="Specify a prefix for the printed string.",
    dest="prefix",
    default="",
)
my_parser.add_argument(
    "-suf",
    "--suffix",
    help="Specify a suffix for the printed string.",
    dest="suffix",
    default="",
)
my_parser.add_argument(
    "-ar",
    "--disable-arrow",
    help="Disable the arrow icon.",
    dest="arrow",
    action="store_true",
)
my_parser.add_argument(
    "-up",
    "--up-arrow",
    help="Change the 'up'-arrow character.",
    dest="upArrow",
    default="↗",
)
my_parser.add_argument(
    "-dw",
    "--down-arrow",
    help="Change the 'down'-arrow character.",
    dest="downArrow",
    default="↘",
)
# Parse arguments
args = my_parser.parse_args()

# Check cache file integrity:
# Create new file with fallback entries
# if it has bad syntax or if it doesn't exist yet.
try:
    with open("coronaCache", "r") as f:
        cachedData_json = json.loads(f.read())
    int(cachedData_json["number"])
    str(cachedData_json["arrow"])
except:
    with open("coronaCache", "w") as f:
        f.write(json.dumps({"number": 0, "arrow": args.upArrow}))


try:
    # Get the API-Response as JSON
    with urllib.request.urlopen(
        f"https://api.covid19api.com/live/country/{args.country}/status/confirmed"
    ) as response:
        json_response = json.loads(response.read().decode("utf-8"))

except TimeoutError:
    # If we have no internet we use the cached file to fetch the data.
    with open("coronaCache", "r") as f:
        cachedData_json = json.loads(f.read())

        cachedNumber = cachedData_json["number"]
        cachedArrow = cachedData_json["arrow"]

        # Print our string to polybar
        print(f"{args.prefix}{cachedNumber}{cachedArrow}{args.suffix}")
        # Don't continue script
        exit()

# We Parse the JSON here
if args.province:
    # Get provice's case numbers if we provided one in arguments
    for province in json_response:
        if province["Province"] == args.province:
            number = province["Active"]
            break
else:
    # Get numbers of all of the country:
    # add together all cases in provinces of country
    number = 0
    for province in json_response:
        number += province["Active"]

# Fallback value for arrow if
# it doesn't get specified below
arrow = ""

if not args.arrow:
    with open("coronaCache", "r") as f:
        cachedData_json = json.loads(f.read())
        cachedNumber = cachedData_json["number"]
        cachedArrow = cachedData_json["arrow"]

    # Get the correct arrow for the tweet
    if cachedNumber != number:
        if number > cachedNumber:
            arrow = args.upArrow

        elif number < cachedNumber:
            arrow = args.downArrow
    else:
        arrow = cachedArrow

# Print result to polybar
print(f"{args.prefix}{number}{arrow}{args.suffix}")


# Save cache to file
with open("coronaCache", "w") as f:
    f.write(json.dumps({"number": number, "arrow": arrow}))
