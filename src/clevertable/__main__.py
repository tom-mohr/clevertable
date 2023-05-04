from .ConversionProfile import ConversionProfile


def run(source_file: str, output_file: str, ignore_columns: list[str]):
    ignore_profile = {col_name: None for col_name in ignore_columns}
    profile = ConversionProfile(ignore_profile)
    df = profile.fit_transform(source_file)

    # choose the output format based on the file extension
    if output_file.endswith(".xlsx"):
        df.to_excel(output_file)
    elif output_file.endswith(".csv"):
        df.to_csv(output_file)
    elif output_file.endswith(".tsv"):
        df.to_csv(output_file, sep="\t")
    else:
        raise ValueError(f"Unexpected file extension: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Consistent and intelligent conversion of tabular data into numerical values.")
    parser.add_argument("src", type=str, help="Path to input file.")
    parser.add_argument("out", type=str, help="Path to output file.")
    parser.add_argument("-i", "--ignore", type=str, nargs="+", default=[], help="Column names to ignore.")

    args = parser.parse_args()

    run(source_file=args.src,
        output_file=args.out,
        ignore_columns=args.ignore)


if __name__ == "__main__":
    main()
