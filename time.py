import datetime
import geopy.distance
import pandas as pd
desired_width = 1000
from pyproj import Proj

"""Pandas Settings for display"""
pd.set_option('display.width', desired_width)
pd.set_option('max_columns', 20)
pd.options.display.float_format = "{:,.8f}".format

def gpstoweekseconds(gps, leapseconds):
    """ Returns the GPS week, the GPS day, and the seconds 
        and microseconds since the beginning of the GPS week """

    datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00.00", datetimeformat)
    tdiff = gps - epoch + datetime.timedelta(seconds=leapseconds)
    gpsweek = tdiff.days // 7
    gpsdays = tdiff.days - 7 * gpsweek
    gpsseconds = tdiff.seconds + 86400 * (tdiff.days - 7 * gpsweek)
    secdiff = gpsseconds + tdiff.microseconds/1000000
    return secdiff


def date1(date):
    datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
    date_f = datetime.datetime.strptime(date, datetimeformat)
    return date_f

def converter(csv_file, mrk_file, mrk_file2, out_csv, text_img):
    # read the position csv from TBC
    csv_data = pd.read_csv(csv_file, header=None)

    # change the time format to match the MRK
    csv_data[5] = csv_data[5].apply(lambda x: gpstoweekseconds(date1(x), 0))

    print(csv_data)

    # Read in the MRK file
    with open(mrk_file, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('	', ',')
    filedata = filedata.replace(' ', '')
    filedata = filedata.replace('[', '')
    filedata = filedata.replace(']', '')

    # Write the file out again
    with open( mrk_file2, 'w') as file:
      file.write(filedata)

    # read the new MRK in csv format
    mrk_data = pd.read_csv( mrk_file2, header=None)
    print(mrk_data)

    # inputs from csv
    input_lat = csv_data[1][0]
    input_lon = csv_data[2][0]
    input_el = csv_data[3][0]
    input_times = csv_data[5]

    # coords lat long degrees longitudes in m
    coords_11 = (input_lat, input_lon)
    coords_22 = (input_lat+1, input_lon)
    coords_33 = (input_lat, input_lon+1)

    lat_deg_in_m = geopy.distance.geodesic(coords_11, coords_22).m
    print(lat_deg_in_m)

    lon_deg_in_m = geopy.distance.geodesic(coords_11, coords_33).m
    print(lon_deg_in_m)

    # iterate to create the new dataframe from the csv with the interpolated pos
    i = 1
    jpg = '.jpg'
    values_df = pd.DataFrame(index=None, columns=None)
    values_df = values_df.fillna(0)

    for idx, row in mrk_data.iterrows():
        input_t = row[1]
        input_n = row[3]
        input_e = row[5]
        input_h = row[7]
        # extract the closest times
        closest = csv_data.iloc[(input_times-input_t).abs().argsort()[:2]]
        closest = closest.reset_index(drop=True)
        closest = closest.sort_values(by=[5])

        print(closest)
        print(closest[5][1])
        print(closest[5][0])

        # percentage calc
        percent_time = ((input_t - closest[5][0])/(closest[5][1] - closest[5][0]))
        print(percent_time)

        # interpolated values
        interpol_lat = (closest[1][0]*(1-percent_time)) + (closest[1][1]*percent_time)
        print(interpol_lat)

        interpol_lon = (closest[2][0]*(1-percent_time)) + (closest[2][1]*percent_time)
        print(interpol_lon)

        interpol_el = (closest[3][0]*(1-percent_time)) + (closest[3][1]*percent_time)
        print(interpol_el)

        # orientation values from the IMU
        lat_diff = input_n/1000/lat_deg_in_m
        lon_diff = input_e/1000/lon_deg_in_m
        ele_diff = input_h/1000

        # new values
        new_lat = interpol_lat + lat_diff
        new_lon = interpol_lon + lon_diff
        new_ele = interpol_el + ele_diff
        ZoneNo = "19"  # Manually input, or calcuated from Lat Lon
        myProj = Proj("+proj=utm +zone=" + ZoneNo + " +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")  # north for north hemisphere
        x, y = myProj( new_lon, new_lat)
        values_temp_df = pd.DataFrame([[i, round(x,ndigits=3), round(y,ndigits=3), round(new_ele, ndigits=3)]], index=None, columns=None)
        values_temp_df[0] = values_temp_df[0].apply(lambda x: '{0:0>4}'.format(x))
        values_temp_df[0] = text_img + values_temp_df[0].astype(str) + jpg
        values_df = values_df.append(values_temp_df, ignore_index=True)
        i = i + 1

    print(values_df)
    values_df.to_csv(out_csv, index=False, header=False)
    return values_df


v01 = converter('V03.csv', 'V03_100_0001_Timestamp.MRK', 'V03_100_0001_Timestamp2.csv', 'FV03.csv', 'V03_100_0001_')
v02 = converter('V04.csv', 'V04_100_0006_Timestamp.MRK', 'V04_100_0006_Timestamp2.csv', 'FV04.csv', 'V04_100_0006_')


