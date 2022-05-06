#======================================================================
import pandas as pd
from tqdm import tqdm
from scipy.spatial import distance

#======================================================================
# Load friendly facilities
df = pd.read_csv("datas/base_data_final.csv", encoding="utf-8")
# Load house data
df2 = pd.read_csv("datas/seoul_pri_2020_ll.csv", encoding="utf-8")

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
                                    #'0.1km편의점', '0.3km편의점', '0.5km편의점',
                                    '0.5km버스정류장', '1.0km버스정류장', '1.5km버스정류장',
                                     '건물면적', '건물금액', '건물주용도'])
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
        dist.append(
            make_km(distance.euclidean((house_lon, house_lat), (friendly_lons[i], friendly_lats[i]))))
        
    ret = []
    for ran in range_list:
        ret.append(count_in_distance(dist, ran))
        
    return ret # list

#======================================================================
selection = ['공원', '도서관', '초등학교', '중학교', '고등학교', '지진옥외대피소', '응급실']
selection2 = ['지하철', '병원', '버스정류장'
            #, '편의점'
             ]
selection_range = [[0.5, 1, 1.5],
                   [1, 2.5],
                   [0.5, 1, 1.5]
                   #,[0.1, 0.3, 0.5]
                  ]

################################################################################################

for j in tqdm(range(len(df2['longitude'])), desc="Progress", mininterval=0.1):
    ret = []

    # append min dist facilities
    for i in range(len(selection)):
        filt = df['구분'] == selection[i]
        ret.append(least_distance_friendly(df2['longitude'][j], df2['latitude'][j], df[filt]['longitude'].values, df[filt]['latitude'].values))

    # append range facilities
    for k in range(len(selection2)):
        filt = df['구분'] == selection2[k]
        temp = num_by_distance(df2['longitude'][j], df2['latitude'][j], df[filt]['longitude'].values, df[filt]['latitude'].values, selection_range[k])
        for tmp in temp:
            ret.append(tmp)

    # add them in dataframe
    df_complete = df_complete.append(pd.Series(ret, index=df_complete.columns[:-3]), ignore_index=True)

    if (j%10000==0):
        df_complete.to_csv("min_distance_columns.csv", encoding="utf-8")

# append house_price and etc..
df_complete['건물면적', '건물금액', '건물주용도'] = df2['건물면적', '물건금액', '건물주용도']


df_complete.to_csv("min_distance_columns.csv", encoding="utf-8")

#======================================================================
