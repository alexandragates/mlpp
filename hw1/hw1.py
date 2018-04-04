from shapely.geometry import Point
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import geopandas as gpd
import requests

# import data and get tables to have the same columns for merging
# vacant table cleaning
vacant_data = pd.read_csv('data/vacant_abandonded.csv')
vacant_data.columns = [c.lower().replace(' ', '_') for c in vacant_data.columns]
vacant_data['street_address'] = vacant_data['address_street_number'].map(str) + " " + vacant_data['address_street_direction'] + " " + vacant_data['address_street_name'] + " " + vacant_data['address_street_suffix']
vacant_data = vacant_data.drop(columns=['location_of_building_on_the_lot_(if_garage,_change_type_code_to_bgd).', 
	'is_the_building_dangerous_or_hazardous?', 'is_building_open_or_boarded?', 'if_the_building_is_open,_where_is_the_entry_point?', 
	'is_the_building_currently_vacant_or_occupied?', 'is_the_building_vacant_due_to_fire?', 'address_street_number', 'address_street_direction', 'address_street_name', 'address_street_suffix'])
vacant_data = vacant_data.rename(index=str, columns={'any_people_using_property?_(homeless,_childen,_gangs)':'subtype', 
	'date_service_request_was_received':'creation_date', 'service_request_type':'type_of_service_request'})
vacant_data = vacant_data.replace({"subtype":{True:"vacant"}})
vacant_data = vacant_data.replace({"subtype":{False:"filled"}})
vacant_data["completion_date"] = np.nan
vacant_data["status"] = np.nan


# alley table cleaning
alley_data = pd.read_csv('data/alley.csv')
alley_data.columns = [c.lower().replace(' ', '_') for c in alley_data.columns]
alley_data["subtype"] = np.nan


# graffiti table cleaning
graffiti_data = pd.read_csv('data/graffiti.csv')
graffiti_data.columns = [c.lower().replace(' ', '_') for c in graffiti_data.columns]
graffiti_data = graffiti_data.rename(index=str, columns={'what_type_of_surface_is_the_graffiti_on?':'subtype'})
graffiti_data = graffiti_data.drop(columns=['ssa','where_is_the_graffiti_located?'])


# merge data and filter for 2017 data only
vacant_plus_alley = pd.concat([vacant_data, alley_data])
all_data = pd.concat([vacant_plus_alley, graffiti_data])
all_data_2017 = all_data[all_data['creation_date'].str.contains('2017')]
all_data_2017.loc[:,['zip_code']] = all_data_2017.loc[:,['zip_code']].fillna(0).astype(int)
all_data_2017.loc[:,['ward']] = all_data_2017.loc[:,['ward']].fillna(0).astype(int)
all_data_2017.loc[:,['police_district']] = all_data_2017.loc[:,['police_district']].fillna(0).astype(int)
all_data_2017.loc[:,['community_area']] = all_data_2017.loc[:,['community_area']].fillna(0).astype(int)
all_data_2017.to_csv('all_data_2017.csv')


# problem 1.2: summary statistics
# request of each type (buildings, alley, graffiti) broken down by:
    # month
    # neighborhood by:
        # zip code
        # police district
    # response time by ciy where possible

# re-format date columns
all_data_2017['creation_date'] = pd.to_datetime(all_data_2017['creation_date'],format='%m/%d/%Y')
all_data_2017['completion_date'] = pd.to_datetime(all_data_2017['completion_date'],format='%m/%d/%Y')
all_data_2017.index = all_data_2017['creation_date']

# how many requests for each type by month
group_time = all_data_2017.groupby([all_data_2017.index.month, 'type_of_service_request'])
group_time = group_time['type_of_service_request'].count().unstack()
group_time.style

plt.figure(); group_time.plot();

# number of requests for each type by zip code
group_zipcode = all_data_2017.groupby(['zip_code', 'type_of_service_request'])
group_zipcode = group_zipcode['zip_code'].count().unstack()
group_zipcode.style

# number of requests for each type by police district
group_policedist = all_data_2017.groupby(['police_district', 'type_of_service_request'])
group_policedist = group_policedist['police_district'].count().unstack()
group_policedist.style

plt.figure(); group_policedist.plot.bar(stacked = False);

# request of subtypes for buildings and graffiti broken down by:
    # month
    # neighborhood by:
        # zip code
        # police district
    # response time by ciy where possible

group_time = all_data_2017.groupby(by=[all_data_2017.index.month, 'subtype', 'type_of_service_request'])
group_time = group_time['subtype'].count().unstack()
group_time.style

group_subtype_zipcode = all_data_2017.groupby(['zip_code', 'subtype', 'type_of_service_request',])
group_subtype_zipcode = group_subtype_zipcode['subtype'].count().unstack()
group_subtype_zipcode.style

group_subtype_policedist = all_data_2017.groupby(['police_district', 'subtype', 'type_of_service_request'])
group_subtype_policedist = group_subtype_policedist['subtype'].count().unstack()
group_subtype_policedist.style

# problem 1.3: 5 things I learned
    # 1. The barchart for counts of each service type by police district shows that different types of crime occur 
        # in different neighborhoods. When the relative count of Graffiti Removal spikes, but the counts for Alley Lights 
        # Out and Vacant/Abandonded do not.
    # 2. The line graph shows that requests for all three types decrease in December and pick up after the new year. 
        # Also, that graffiti removal requests spike when the weather is nicer, with the largest spike in September. 
        # Alley light requests are increased in winter, and are highest in November, around the time clocks are changed 
        # for daylights saving putting more people are out after dark.
    # 3. The barchart for counts of each service type by police district shows that police districts in the south and west sides 
        # (4, 5, 6, 7, 8) are more likely to have reports of vacant buildings, whereas reports for Alley Light Out and Graffiti 
        # Removal are some in the west (specifically district 8 has a high reporting for Graffiti Removal), but mostly in the 
        # north side.
    # 4. The most common subtype for Graffiti Removal requests is metal-painted.
    # 5. If an building is reported vacant/abandonded, it is more likely to be reported as filled than vacant.

# problem 2
# pull data from ACS API for race (race total, white alone, black alone, hispanic total, income, family size...
acs_data = pd.read_json("https://api.census.gov/data/2016/acs/acs5?get=NAME,B02001_001E,B02001_002E,B02001_003E,B03001_001E,B03001_002E,B03001_003E,B03001_004E,B03001_005E,B19001_001E,B19001_002E,B19001_003E,B19001_004E,B19001_005E,B19001_006E,B19001_007E,B19001_008E,B19001_009E,B19001_010E,B19001_011E,B19001_012E,B19001_013E,B19001_014E,B19001_015E,B19001_016E,B19001_017E,B11016_001E,B11016_002E,B11016_009E&for=block+group:*&in=state:17+county:031+tract:*&key=17c33afc69e74a76256559f11768a4005763e816")
col_names=["name", "total_race", "white_alone", "black_alone", "total_ethnic", "non_hisp", "hisp", "mexican", "puerto_rican", "total_household_inc", "<10k", "10-14.9k", "15-19.9k", "20-24.9k", "25-29.9k", "30-34.9k", "35-39.9k", "40-44.9k", "45-49.9k", "50-59.9k", "60-74.9k", "75-99.9k", "100-124.9k", "125-149.9k", "150-199.9k", "200k+", "total_household_type_by_size", "household_type_family_household", "household_type_nonfamily_household","state","county","tract","block_group"]
acs_data.columns = col_names
acs_data["GEOID"] = acs_data["state"] + acs_data["county"] + acs_data["tract"] + acs_data["block_group"]
acs_data = acs_data.drop([0])
columns_to_change = ["total_race", "white_alone", "black_alone", "total_ethnic", "non_hisp", "hisp", "mexican", "puerto_rican", 
           "total_household_inc", "<10k", "10-14.9k", "15-19.9k", "20-24.9k", "25-29.9k", "30-34.9k", "35-39.9k", "40-44.9k", 
           "45-49.9k", "50-59.9k", "60-74.9k", "75-99.9k", "100-124.9k", "125-149.9k", "150-199.9k", "200k+", 
           "total_household_type_by_size", "household_type_family_household", "household_type_nonfamily_household"]

for x in columns_to_change:
    acs_data[x]=acs_data[x].fillna(0)
    acs_data[x] = acs_data[x].astype(int)

acs_data['percent_white'] = acs_data["white_alone"]/acs_data["total_race"]
acs_data['percent_black'] = acs_data["black_alone"]/acs_data["total_race"]
acs_data['percent_non_hisp'] = acs_data["non_hisp"]/acs_data["total_ethnic"]
acs_data['percent_hisp'] = acs_data["hisp"]/acs_data["total_ethnic"]
acs_data['percent_mexican'] = acs_data["mexican"]/acs_data["total_ethnic"]
acs_data['percent_puerto_rican'] = acs_data["puerto_rican"]/acs_data["total_ethnic"]
acs_data['percent_<10k'] = acs_data["<10k"]/acs_data["total_household_inc"]
acs_data['percent_10_14.9k'] = acs_data["10-14.9k"]/acs_data["total_household_inc"]
acs_data['percent_15_19.9k'] = acs_data["15-19.9k"]/acs_data["total_household_inc"]
acs_data['percent_20_24.9k'] = acs_data["20-24.9k"]/acs_data["total_household_inc"]
acs_data['percent_25_29.9k'] = acs_data["25-29.9k"]/acs_data["total_household_inc"]
acs_data['percent_30_34.9k'] = acs_data["30-34.9k"]/acs_data["total_household_inc"]
acs_data['percent_35_39.9k'] = acs_data["35-39.9k"]/acs_data["total_household_inc"]
acs_data['percent_40_44.9k'] = acs_data["40-44.9k"]/acs_data["total_household_inc"]
acs_data['percent_45_49.9k'] = acs_data["45-49.9k"]/acs_data["total_household_inc"]
acs_data['percent_50_59.9k'] = acs_data["50-59.9k"]/acs_data["total_household_inc"]
acs_data['percent_60_74.9k'] = acs_data["60-74.9k"]/acs_data["total_household_inc"]
acs_data['percent_75_99.9k'] = acs_data["75-99.9k"]/acs_data["total_household_inc"]
acs_data['percent_100_124.9k'] = acs_data["100-124.9k"]/acs_data["total_household_inc"]
acs_data['percent_125_149.9k'] = acs_data["125-149.9k"]/acs_data["total_household_inc"]
acs_data['percent_150_199.9k'] = acs_data["150-199.9k"]/acs_data["total_household_inc"]
acs_data['percent_200k+'] = acs_data["200k+"]/acs_data["total_household_inc"]
acs_data['percent_household_type_family_household'] = acs_data["household_type_family_household"]/acs_data["total_household_type_by_size"]
acs_data['percent_household_type_nonfamily_household'] = acs_data["household_type_nonfamily_household"]/acs_data["total_household_type_by_size"]

# grab block group TIGER shapefile from census and merge with ACS data on ID
shp_data = gpd.read_file("tiger_files/")
acs_with_shp = pd.merge(acs_data, shp_data, on="GEOID")

# use geopandas spatial join to map lat-longs from chicago open data to polygons for block groups from the shapefile
all_data_2017 = all_data_2017.dropna(subset=['latitude','longitude']) 
geometry = [Point(xy) for xy in zip(all_data_2017.longitude, all_data_2017.latitude)]
all_data_2017_geo = all_data_2017.drop(['longitude', 'latitude'], axis=1)
all_data_geo = gpd.GeoDataFrame(all_data_2017_geo, geometry=geometry)
acs_with_shp_geo = gpd.GeoDataFrame(acs_with_shp)
acs_311_shp = gpd.sjoin(all_data_geo, acs_with_shp_geo)
acs_311_shp.head()

# problem 2.a What types of blocks get “Vacant and Abandoned Buildings Reported”?

# The analysis looked at the race, ethnicitiy, household income and household type for blocks that 
# reported vacant and abandonded building. 

# Race: There is a very clear divide. The average percent of white residents living on a block that 
# reported a vacant or abandonded building was 11.6%, compared to an average of 80.5% black residents.

# Ethnicity: While I expected there to be a difference among hispanic and non-hispanic, and was interested in differences
# between Puerto Rican and Mexican neighborhoods around Chicago, this data did not yeild any results.

# Household Income: This variable shows that blocks with the lowest income populations see more reporting of vacant and 
# abandoned buildings. Speicifically, the share of blocks reported that had incomes below $10,000 a year was 
# almost 17%. Overall, th average percent of blocks reporting vacant or abandonded buildings decreased as the income increased,
# however, the average increases, compared to the incomes immediately below and above this range, for incomes betweem 
# $50,000 and $100,000. The average then decreases again.

# Household Type: Here there is also a difference between family household types and non-family household types. Family household
# types see an average of 63%, whereas non-family household types see an average of 36%. 

# code to answer above question: filter by Vacant and Abandoned Buildings Reported and run basic stats
acs_311_shp_buildings = acs_311_shp.loc[acs_311_shp['type_of_service_request'] == 'Vacant/Abandoned Building']

columns = ["empty"]

# basic stats for race
to_describe_race = ['percent_white', 'percent_black']
df_race_buildings = pd.DataFrame(columns=columns)
df_race_buildings = df_race_buildings.fillna(0)

for x in to_describe_race:
    df_to_add = acs_311_shp_buildings[x].describe()
    df_race_buildings = pd.concat([df_race_buildings, df_to_add], axis=1)
print(df_race_buildings)

#basic stats for ethnic
to_describe_ethnic = ['percent_non_hisp', 'percent_hisp', 'percent_mexican', 'percent_puerto_rican']
df_ethnic_buildings = pd.DataFrame(columns=columns)
df_ethnic_buildings = df_ethnic_buildings.fillna(0)

for x in to_describe_ethnic:
    df_to_add = acs_311_shp_buildings[x].describe()
    df_ethnic_buildings = pd.concat([df_ethnic_buildings, df_to_add], axis=1)
print(df_ethnic_buildings)

# basic stats for household income
to_describe_household_inc = ['percent_<10k', 'percent_10_14.9k', 'percent_15_19.9k', 'percent_20_24.9k', 'percent_25_29.9k', 'percent_30_34.9k', 'percent_35_39.9k', 'percent_40_44.9k', 'percent_45_49.9k', 'percent_50_59.9k', 'percent_60_74.9k', 'percent_75_99.9k', 'percent_100_124.9k', 'percent_125_149.9k', 'percent_150_199.9k', 'percent_200k+']
df_household_inc_buildings = pd.DataFrame(columns=columns)
df_household_inc_buildings = df_household_inc_buildings.fillna(0)

for x in to_describe_household_inc:
    df_to_add = acs_311_shp_buildings[x].describe()
    df_household_inc_buildings = pd.concat([df_household_inc_buildings, df_to_add], axis=1)
print(df_household_inc_buildings)

# basic stats for household type
to_describe_household_type = ['percent_household_type_family_household', 'percent_household_type_nonfamily_household']
df_household_type_buildings = pd.DataFrame(columns=columns)
df_household_type_buildings = df_household_type_buildings.fillna(0)

for x in to_describe_household_type:
    df_to_add = acs_311_shp_buildings[x].describe()
    df_household_type_buildings = pd.concat([df_household_type_buildings, df_to_add], axis=1)
print(df_household_type_buildings)

# problem 2.b What types of blocks get “Alley Lights Out”?

# The analysis looked at the race, ethnicitiy, household income and household type for blocks that 
# reported alley lights out.

# Race: There is not a very clear divide. The average percent of white residents living on a block that 
# reported an out alley light was nearly identical to the average seen for black residents: 40%.

# Ethnicity: While I expected there to be a difference among hispanic and non-hispanic, and was interested in differences
# between Puerto Rican and Mexican neighborhoods around Chicago, this data did not yeild any results.

# Household Income: This variable shows that blocks with the lowest income populations see more reporting of alley lights out. 
# Speicifically, the share of blocks reported that had incomes below $10,000 a year was almost 10%. Overall, the average 
# percent of blocks reporting alley lights out decreased as the income increased, however, the average increases, compared 
# to the incomes immediately below and above this range, for incomes betweem $50,000 and $100,000. 
# The average then decreases again.

# Household Type: Here there is also a difference between family household types and non-family household types. Family household
# types see an average of 65%, whereas non-family household types see an average of 35%. 

# problem 2.b - filter by alley lights out and run basic stats
acs_311_shp_alleys = acs_311_shp.loc[acs_311_shp['type_of_service_request'] == 'Alley Light Out']

# basic stats for race
df_race_alleys = pd.DataFrame(columns=columns)
df_race_alleys = df_race_alleys.fillna(0)

for x in to_describe_race:
    df_to_add = acs_311_shp_alleys[x].describe()
    df_race_alleys = pd.concat([df_race_alleys, df_to_add], axis=1)
print(df_race_alleys)

#basic stats for ethnic
df_ethnic_alleys = pd.DataFrame(columns=columns)
df_ethnic_alleys = df_ethnic_alleys.fillna(0)

for x in to_describe_ethnic:
    df_to_add = acs_311_shp_alleys[x].describe()
    df_ethnic_alleys = pd.concat([df_ethnic_alleys, df_to_add], axis=1)
print(df_ethnic_alleys)

# basic stats for household income
df_household_inc_alleys = pd.DataFrame(columns=columns)
df_household_inc_alleys = df_household_inc_alleys.fillna(0)

for x in to_describe_household_inc:
    df_to_add = acs_311_shp_alleys[x].describe()
    df_household_inc_alleys = pd.concat([df_household_inc_alleys, df_to_add], axis=1)
print(df_household_inc_alleys)

# basic stats for household type
df_household_type_alleys = pd.DataFrame(columns=columns)
df_household_type_alleys = df_household_type_alleys.fillna(0)

for x in to_describe_household_type:
    df_to_add = acs_311_shp_alleys[x].describe()
    df_household_type_alleys = pd.concat([df_household_type_alleys, df_to_add], axis=1)
print(df_household_type_alleys)


# problem 2.c does that change over time in the data you collected?

# The analysis looked specifically at the race and household income for blocks that reported vacant and abandonded building by month.

# Race: While the race data changes by month, there seems to be a pattern for white reporting, but not for black. 
# The average percent of white residents living on a block that reported a vacant or abandonded building increases during winter months,
# compared to summer months. However, this same trend does not seem to hold for blocks with more black residents.

# Household Income: The trends from before hold: blocks with the lowest income populations see more reporting of vacant and 
# abandoned buildings. Speicifically, the share of blocks reported that had incomes below $10,000 a year was 
# fluctuates around 16%. Overall, the average percent of blocks reporting vacant or abandonded buildings decreased as the income increased.

# The analysis looked at the race and household income for blocks reporting alley lights out.

# Race: There is not a very clear divide. The average percent of white residents living on a block that 
# reported an out alley light was nearly identical to the average seen for black residents: 40%. That said, for white, the reporting
# is done mostly in the winter, whereas for black the reporting is done mostly in the summer.

# Household Income: This variable shows that blocks with the lowest income populations see more reporting of alley lights out. 
# Speicifically, the share of blocks reported that had incomes below $10,000 a year was almost 10%, with a generally higher average in the summer.
# Overall, the average percent of blocks reporting alley lights out decreased as the income increased.

# code for problem 2.c - filter by month for stand out variables above
acs_311_shp_buildings['creation_date'] = pd.to_datetime(acs_311_shp_buildings['creation_date'],format='%m/%d/%Y')
acs_311_shp_buildings['completion_date'] = pd.to_datetime(acs_311_shp_buildings['completion_date'],format='%m/%d/%Y')
acs_311_shp_buildings.index = acs_311_shp_buildings['creation_date']

df_race_buildings_time = pd.DataFrame(columns=columns)
df_race_buildings_time = df_race_buildings_time.fillna(0)

for x in to_describe_race:
    group_acs_311_shp_buildings = acs_311_shp_buildings.groupby([acs_311_shp_buildings.index.month, 'type_of_service_request'])
    group_acs_311_shp_buildings = group_acs_311_shp_buildings[x].describe().unstack()
    print("this is for", x, "variable:", group_acs_311_shp_buildings)

for x in to_describe_household_inc:
    group_acs_311_shp_buildings = acs_311_shp_buildings.groupby([acs_311_shp_buildings.index.month, 'type_of_service_request'])
    group_acs_311_shp_buildings = group_acs_311_shp_buildings[x].describe().unstack()
    print("this is for", x, "variable:", group_acs_311_shp_buildings)
    
acs_311_shp_alleys['creation_date'] = pd.to_datetime(acs_311_shp_alleys['creation_date'],format='%m/%d/%Y')
acs_311_shp_alleys['completion_date'] = pd.to_datetime(acs_311_shp_alleys['completion_date'],format='%m/%d/%Y')
acs_311_shp_alleys.index = acs_311_shp_alleys['creation_date']

df_race_alleys_time = pd.DataFrame(columns=columns)
df_race_alleys_time = df_race_alleys_time.fillna(0)

for x in to_describe_race:
    group_acs_311_shp_alleys = acs_311_shp_alleys.groupby([acs_311_shp_alleys.index.month, 'type_of_service_request'])
    group_acs_311_shp_alleys = group_acs_311_shp_alleys[x].describe().unstack()
    print("this is for", x, "variable:", group_acs_311_shp_alleys)

for x in to_describe_household_inc:
    group_acs_311_shp_alleys = acs_311_shp_alleys.groupby([acs_311_shp_alleys.index.month, 'type_of_service_request'])
    group_acs_311_shp_alleys = group_acs_311_shp_alleys[x].describe().unstack()
    print("this is for", x, "variable:", group_acs_311_shp_alleys)


# problem 2.d - What is the difference in blocks that get “Vacant and Abandoned Buildings Reported” vs “Alley Lights Out”?

# The biggest difference between the two is race. For Vacanat and Abandonded Buildings Reported, there is a very clear 
# difference in the types of blocks that are reporting. Namely, blocks reporting are overwhemlingly black.
# Whereas in the Alley Lights Out variable, the blocks reporting are generally similar. Household income and household 
# type were about the same for both variables.


# problem 3a: Of the three types of requests you have data for, which request type is the most likely given the 
# call came from 3600 W Roosevelt Ave? What are the probabilities for each type of request?

# the most likely request type for that address is graffiti. probability for buildings and alleys is 0%, because 
# no requests were made by that address. probability for graffiti is 1/112699.

# search for 3600 W. Roosevelt* in acs_311_shp, 
acs_311_shp_3600 = acs_311_shp[acs_311_shp['street_address'].str.contains('3600 W ROOSEVELT', na=False)]
print(acs_311_shp_3600)

# probability
group_type = acs_311_shp.groupby(['type_of_service_request']).count()


# problem 3b: Let’s now assume that a call comes in about Graffiti Removal. Which is more likely – 
# that the call came from Garfield Park (community areas 26 and 27) or Uptown (community area 3?
# How much more or less likely is it to be from Garfield Park vs Uptown?

# It is more likely that the call came from Uptown than Garfield Park, with Uptown having 1853 calls for graffiti removal
# and Garfield Park having only 454.

acs_311_shp_graffiti = acs_311_shp.loc[acs_311_shp['type_of_service_request'] == 'Graffiti Removal']
acs_311_shp_graffiti.head()
group = acs_311_shp_graffiti.groupby(['community_area']).count()

uptown = group.loc[3, 'street_address']
print(uptown)

garfield1 = group.loc[26, 'street_address']
garfield2 = group.loc[27, 'street_address']
garfield = garfield1 + garfield2
print(garfield)


# problem 3c:
# garfield park = (100/600) * (600/1000) = .1, or 10%
# uptown = (160/400) * (400*1000) = .16, or 16%.

