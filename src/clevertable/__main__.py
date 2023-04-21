from .numerical_converter import NumericalConverter


def main(source_file: str, output_file: str, profile: dict, ignore_unknown: bool):
    nc = NumericalConverter(ignore_unknown=ignore_unknown)
    nc.update_profile(profile)

    df = nc(source_file)

    # choose the output format based on the file extension
    if output_file.endswith(".xlsx"):
        df.to_excel(output_file)
    elif output_file.endswith(".csv"):
        df.to_csv(output_file)
    else:
        raise ValueError(f"Unexpected file extension: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str, help="Path to source file")
    parser.add_argument("out", type=str, help="Path to output file")
    parser.add_argument("--profile", type=str, default=None, help="Path to JSON profile file")
    parser.add_argument("--ignore-unknown", action="store_true", help="Ignore unknown columns")

    args = parser.parse_args()

    if args.profile is not None:
        # load profile from file
        import json
        with open(args.profile, "r") as f:
            profile = json.load(f)
    else:
        profile = {}

    main(source_file=args.src,
         output_file=args.out,
         profile=profile,
         ignore_unknown=args.ignore_unknown)
