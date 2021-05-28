#!/usr/bin/env python3
import argparse, json, urllib.request, os, locale, sys


def get_api_json(url: str):
    # Get the API-Response as JSON
    with urllib.request.urlopen(url) as response:
        json_response = json.loads(response.read().decode("utf-8"))
        response_code = response.getcode()
    if response_code != 200:
        raise ConnectionError
    return json_response


def get_cache(cachePath):
    with open(cachePath, "r") as f:
        data = json.loads(f.read())
        number = data["number"]
        arrow = data["arrow"]
    return {"number": number, "arrow": arrow}


# Create the parser
my_parser = argparse.ArgumentParser()

# Add the arguments
my_parser.add_argument(
    "country",
    help="Specify the country you want to display.",
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
    "--enable-arrow",
    help="Enable the arrow icon.",
    dest="arrow",
    action="store_true",
)

my_parser.add_argument(
    "-up",
    "--up-arrow",
    help="Change the 'up'-arrow character.",
    dest="upArrow",
    default=" ↗",
)

my_parser.add_argument(
    "-dw",
    "--down-arrow",
    help="Change the 'down'-arrow character.",
    dest="downArrow",
    default=" ↘",
)

my_parser.add_argument(
    "-lo",
    "--enable-locale",
    help="Enable decimal points.",
    dest="locale",
    action="store_true",
)

# Parse arguments
args = my_parser.parse_args()

# Define the path the cache goes to:
cachePath = os.path.join(
    os.path.join(os.environ.get("HOME"), ".cache"),
    os.path.join(
        "coronaWidgetPolybar",
        "coronaCache",
    ),
)

# Check cache file integrity:
# Create new file with fallback entries
# if it has bad values or if it doesn't exist yet.
try:
    with open(cachePath, "r") as f:
        cachedData_json = json.loads(f.read())

    # make sure that values have the right data-type
    int(cachedData_json["number"])
    bool(cachedData_json["arrow"])

    # Reset cache if changing country
    if cachedData_json["country"] != args.country:
        raise
    # Reset cache if changing province
    if cachedData_json["province"] != args.province:
        raise
except:
    # Create path for the file if we have to
    if not os.path.exists(os.path.dirname(cachePath)):
        os.makedirs(os.path.dirname(cachePath))

    # Write fallback values
    with open(cachePath, "w") as f:
        f.write(
            json.dumps(
                {
                    "country": args.country,
                    "province": args.province,
                    "number": 0,
                    "arrow": True,
                }
            )
        )

# get data from API
try:
    if args.province:
        response = get_api_json(
            f"https://api.covid19api.com/live/country/{args.country}/status/confirmed"
        )

        # get latest value for given province
        found = False
        for timestamp in response:
            if timestamp["Province"] == args.province:
                number = timestamp["Active"]
                found = True
        if found == False:
            raise Exception("Province not found!")
    else:
        response = get_api_json(
            f"https://api.covid19api.com/total/country/{args.country}"
        )

        # get latest item
        latest = response[len(response) - 1]
        number = latest["Active"]

except ConnectionError:
    # If we have no internet / the API is down
    # we use the cached file to fetch the data.
    cache = get_cache(cachePath)

    number = cache["number"]
    arrow = cache["arrow"]

    # Print our string to polybar
    print(f"{args.prefix}{number}{arrow}{args.suffix}")

    # Don't continue script
    sys.exit()

# Load data from cache to have
# something to compare to
cache = get_cache(cachePath)

# Get the correct arrow to display
# arrowBool: True is up; False is down
if cache["number"] == number:
    arrowBool = cache["arrow"]
elif number > cache["number"]:
    arrowBool = True
else:
    arrowBool = False

# Get the correct arrow symbol from arguments
if arrowBool:
    arrowStr = args.upArrow
else:
    arrowStr = args.downArrow

# Save new cache to file
with open(cachePath, "w") as f:
    f.write(
        json.dumps(
            {
                "country": args.country,
                "province": args.province,
                "number": number,
                "arrow": arrowBool,
            }
        )
    )

# Don't print arrow if not enabled in arguments
if not args.arrow:
    arrowStr = ""

# Print with locale seperators if enabled
if args.locale:
    locale.setlocale(locale.LC_ALL, "")
    number = "{0:n}".format(number)

# Print result to polybar
print(f"{args.prefix}{number}{arrowStr}{args.suffix}")
