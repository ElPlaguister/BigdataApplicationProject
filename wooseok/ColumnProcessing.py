#======================================================================
import pandas as pd
from tqdm import tqdm
import numpy as np
from scipy.spatial import distance

#======================================================================
# Load friendly facilities
df = pd.read_csv("datas/base_data_final.csv", encoding="utf-8")
# Load house data
df2 = pd.read_csv("datas/seoul_pri_2019_ll.csv", encoding="utf-8")

# data rectify: delete null data
filt = df['longitude'].isnull()
df.drop(index=df[filt].index, inplace=True)
filt2 = df['latitude'].isnull()
df.drop(index=df[filt2].index, inplace=True)

# data rectify: convert longitde from str to float
df['longitude'] = df['longitude'].apply(lambda x: float(x))

#======================================================================
df_complete = pd.DataFrame(columns=['공원최단거리', '도서관최단거리',
                                    '초등학교최단거리', '중학교최단거리', '고등학교최단거리',
                                    '지진옥외대피소최단거리', '응급실최단거리',
                                    '0.5km지하철', '1.0km지하철', '1.5km지하철',
                                    '1.0km병원', '2.5km병원',
                                    '0.1km편의점', '0.3km편의점', '0.5km편의점',
                                    '0.1km버스정류장', '0.3km버스정류장', '0.5km버스정류장',
                                     '건물면적', '건물금액', '건물주용도',
                                     '건물명', 'latitude', 'longitude'])
#======================================================================
# distance's output is not km.
def make_km(x):
    # 2.3f
    return x // 0.00001 /1000

# Input: house 는 데이터 하나, 우호시설은 데이터 column
def least_distance_friendly(house_lon, house_lat, friendly_lons, friendly_lats):
    dist = []
    for i in range(len(friendly_lons)):
        try: 
            dist.append(
                make_km(distance.euclidean((house_lon, house_lat), (friendly_lons[i], friendly_lats[i]))
                ))
        except: 
            dist.append(-999)
    try:
        ret = min(dist)
    except:
        ret = -999
    return ret
def list_element_is_in(base_list, element):
    for i in base_list:
        if len(base_list)==0:
            return False
        if [i] == element:           
            return True
    return False

# count num of friendly facilities in range
# Input: distance list, range list [km]
def st_count_in_distance(dist_list, range_km, station_lines):
    count = 0
    appended_line = []
    
    for i, dist in enumerate(dist_list):
        if 0 < dist < range_km and not list_element_is_in(appended_line, [station_lines[i]]):
            count +=1
            appended_line.append(station_lines[i])
    return count
# Input: house 는 데이터 하나, 우호시설은 데이터 column
def st_num_by_distance(house_lon, house_lat, friendly_lons, friendly_lats, range_list, station_lines):
    dist = []
    for i in range(len(friendly_lons)):
        dist.append(
            make_km(distance.euclidean((house_lon, house_lat), (friendly_lons[i], friendly_lats[i]))))
    
    ret = []
    for ran in range_list:
        ret.append(st_count_in_distance(dist, ran, station_lines))

        
    return ret # list

# count num of friendly facilities in range
# Input: distance list, range list [km]
def count_in_distance(dist_list, range_km):
    count = 0
    for i in dist_list:
        if i < range_km:
            count +=1
    return count

# Input: house 는 데이터 하나, 우호시설은 데이터 column
def num_by_distance(house_lon, house_lat, friendly_lons, friendly_lats, range_list):
    dist = []
    for i in range(len(friendly_lons)):
        try:
            dist.append(
                make_km(distance.euclidean((house_lon, house_lat), (friendly_lons[i], friendly_lats[i]))))
        except:
            dist.append(9999)
    ret = []
    for ran in range_list:
        ret.append(count_in_distance(dist, ran))
        
    return ret # list

#======================================================================
selection = ['공원', '도서관', '초등학교', '중학교', '고등학교', '지진옥외대피소', '응급실']
selection2 = ['지하철', '병원', '버스정류장'
            , '편의점'
             ]
selection_range = [[0.5, 1, 1.5],
                   [1, 2.5],
                   [0.1, 0.3, 0.5]
                   ,[0.1, 0.3, 0.5]
                  ]

csv_file_name = "processed_data_2019.csv"

#======================================================================
for j in tqdm(range(len(df2['longitude'])), desc="Progress", mininterval=0.1):
    ret = []

    # append min dist facilities
    for i in range(len(selection)):
        filt = df['구분'] == selection[i]
        ret.append(least_distance_friendly(df2['longitude'][j], df2['latitude'][j], df[filt]['longitude'].values, df[filt]['latitude'].values))

    # append range facilities
    for k in range(len(selection2)):
        filt = df['구분'] == selection2[k]
        if (selection2[k] == '지하철'):
            temp1 = st_num_by_distance(df2['longitude'][j], df2['latitude'][j], df[filt]['longitude'].values, df[filt]['latitude'].values, selection_range[k], df[filt]['Station_line'].values)
            for tmp in temp1:
                ret.append(tmp)
        else:
            temp2 = num_by_distance(df2['longitude'][j], df2['latitude'][j], df[filt]['longitude'].values, df[filt]['latitude'].values, selection_range[k])
            for tmp in temp2:
                ret.append(tmp)

    # add them in dataframe
    df_complete = df_complete.append(pd.Series(ret, index=df_complete.columns[:-6]), ignore_index=True)

    if (j%10000==0):
        df_complete.to_csv(csv_file_name, encoding="utf-8")

# append house_price and etc..
df_complete[['건물면적', '건물금액', '건물주용도', '건물명', 'latitude', 'longitude']] = df2[['건물면적', '물건금액', '건물주용도', '건물명', 'latitude', 'longitude']]


df_complete.to_csv(csv_file_name, encoding="utf-8")

#======================================================================
