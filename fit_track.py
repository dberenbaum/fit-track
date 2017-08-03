import csv
import pandas as pd
from bs4 import BeautifulSoup


def parse_tcx(filename):
    """Extracts trackpoints from .tcx file and returns list of trackpoints."""

    with open(filename) as infile:
        activity = BeautifulSoup(infile, "xml")
        points = activity.find_all("Trackpoint")
        fields = ["DistanceMeters", "Time", "LatitudeDegrees",
                  "LongitudeDegrees", "AltitudeMeters"]
        points_list = []
        for point in points:
            point_dict = {}
            for field in fields:
                val = ""
                point_field = point.find(field)
                if point_field:
                    val = point_field.string
                point_dict[field] = val
            points_list.append(point_dict)
        return points_list


def write_csv(points, filename):
    """Writes points list to csv."""

    fields = points[0].keys()
    with open(filename, "w") as outfile:
        csvwriter = csv.DictWriter(outfile, fieldnames=fields)
        csvwriter.writeheader()
        csvwriter.writerows(points)


def df_from_points(points):
    """Make a pandas dataframe from points."""
    df = pd.DataFrame(points)
    df = df.replace("", "0")
    for col in df.columns:
        if col == "Time":
            df[col] = pd.to_datetime(df[col])
        else:
            df[col] = df[col].astype(float)
    return df


def mph_by_interval(df, interval):
    """Get MPH by resampling at given interval."""
    df = df.set_index("Time")
    distance = df["DistanceMeters"]
    interval_dist = distance.shift(-1) - distance
    resampled = interval_dist.resample(interval).sum()
    mph = (resampled/1609.34)/(interval.total_seconds()/3600.)
    return mph


def trim_mph(df, quantile=0.25):
    """
    Trim MPH dataframe by removing consecutive leading and trailing points
    less than quantile. This helps remove erroneous points that actually
    occurred before or after the activity.
    """
    cutoff = df.quantile(quantile)
    gt_cutoff = df[df > cutoff]
    start = gt_cutoff.index[0]
    end = gt_cutoff.index[-1]
    return df[start:end]


def modify_destination(df, lat, lon):
    """
    Modify the destination of an out-and-back workout. This helps correct
    activity data where no data point was captured near the outermost point of
    the activity.
    """
    pass


def get_destination(df):
    """Get the index of the destination of an out-and-back workout."""
    coords = df[["LatitudeDegrees", "LongitudeDegrees"]]
    coords = coords[(coords["LatitudeDegrees"] != 0) &
                    (coords["LongitudeDegrees"] != 0)]
    moves = coords.shift(-1) - coords
    # TODO: replace rolling mean with lowess curve.
    moves_smooth = moves.rolling(window=window, center=True).mean().dropna()
    dirs = moves_smooth > 0
    dir_shifts = (dirs.shift(-1) - dirs).dropna()
    inflection = dir_shifts[(dir_shifts["LatitudeDegrees"] != 0) &
                            (dir_shifts["LongitudeDegrees"] != 0)]
    if len(inflection) == 1:
        dest_pt = inflection.index.values[0]
    return dest_pt
