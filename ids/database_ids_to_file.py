# Read IDs from a MaterialDatabase and write them to STDOUT

from  madas import MaterialsDatabase

from argparse import ArgumentParser

def get_argument_parser():
    argparser = ArgumentParser(description="Read IDs from a MaterialDatabase and write them to STDOUT.")

    argparser.add_argument("--input-file",
                           help="MaterialsDatabase file to read IDs",
                           required=True,
                           type=str,
                           dest="infile")
    
    argparser.add_argument("--input-path",
                           help="Relative path to database file. Default: '.'",
                           required=False,
                           type=str,
                           default=".",
                           dest="inpath")
    
    argparser.add_argument("--comment",
                           help="Comment to include in output file",
                           required=False,
                           type=str,
                           default=None,
                           dest="comment")
    return argparser

def main():
    argparser = get_argument_parser()

    args = argparser.parse_args()

    db = MaterialsDatabase(filename=args.infile, filepath=args.inpath)

    output = f"# {args.comment}\n" if args.comment is not None else ""
    output += "\n".join([entry.mid for entry in db])

    print(output)

if __name__ == "__main__":
    main()