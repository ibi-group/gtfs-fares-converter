import argparse

from convert import convert_fares

def main():
    parser = argparse.ArgumentParser(
        description="Converts a GTFS feed's Fares V1 info to Fares V2 info."
    )
    parser.add_argument(
        "input_zip",
        help="Path to the current GTFS zip file."
    )
    parser.add_argument(
        "output_zip",
        help="Path to the output zip file."
    )
    args = parser.parse_args()
    convert_fares(args.input_zip, args.output_zip)

if __name__ == "__main__":
    main()
