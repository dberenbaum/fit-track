import argparse
import os

import fit_track


def main():
    parser = argparse.ArgumentParser(description="extract trackpoints from .tcx \
                                     file and save as .csv")
    parser.add_argument("--infile", "-i", required=True, help="path to .tcx file.")
    parser.add_argument("--outfile", "-o", help="path to .csv file for writing.")
    args = parser.parse_args()
    tcxfile = args.infile
    csvfile = args.outfile

    points = fit_track.parse_tcx(tcxfile)
    if not csvfile:
        basename = os.path.splitext(tcxfile)[0]
        csvfile = basename + ".csv"
    fit_track.write_csv(points, csvfile)


if __name__ == "__main__":
    main()
