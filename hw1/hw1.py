import pandas as pd
import numpy as np

# problem 1.1

# import data and get tables to have the same columns for merging
# vacant table cleaning
vacant_data = pd.read_csv('data/vacant_abandonded.csv')
vacant_data.columns = [c.lower().replace(' ', '_') for c in vacant_data.columns]
vacant_data = vacant_data.drop(columns=['location_of_building_on_the_lot_(if_garage,_change_type_code_to_bgd).', 
	'is_the_building_dangerous_or_hazardous?', 'is_building_open_or_boarded?', 'if_the_building_is_open,_where_is_the_entry_point?', 
	'is_the_building_currently_vacant_or_occupied?', 'is_the_building_vacant_due_to_fire?', 'address_street_number', 
	'address_street_direction', 'address_street_name', 'address_street_suffix'])
vacant_data = vacant_data.rename(index=str, columns={'any_people_using_property?_(homeless,_childen,_gangs)':'subtype', 
	'date_service_request_was_received':'creation_date', 'service_request_type':'type_of_service_request'})
vacant_data = vacant_data.replace({"subtype":{True:"vacant"}})
vacant_data = vacant_data.replace({"subtype":{False:"filled"}})
vacant_data["completion_date"] = np.nan
vacant_data["status"] = np.nan
#print(vacant_data)
#print(list(vacant_data), "vacant_data")

# alley table cleaning
alley_data = pd.read_csv('data/alley.csv')
alley_data.columns = [c.lower().replace(' ', '_') for c in alley_data.columns]
alley_data["subtype"] = np.nan
alley_data = alley_data.drop(columns=['street_address'])
#print(alley_data)
#print(list(alley_data), "alley_data")

# graffiti table cleaning
graffiti_data = pd.read_csv('data/graffiti.csv')
graffiti_data.columns = [c.lower().replace(' ', '_') for c in graffiti_data.columns]
graffiti_data = graffiti_data.rename(index=str, columns={'what_type_of_surface_is_the_graffiti_on?':'subtype'})
graffiti_data = graffiti_data.drop(columns=['street_address', 'ssa','where_is_the_graffiti_located?'])
#print(graffiti_data)
#print(list(graffiti_data), "graffiti_data")

# merge data
vacant_plus_alley = pd.concat([vacant_data, alley_data])
all_data = pd.concat([vacant_plus_alley, graffiti_data])
print(all_data)
print(list(all_data), "all_data")




#vacant_data = vacant_data.rename(str.lower, axis='columns')
#vacant_data.columns = [c.lower().replace(' ', '_') for c in vacant_data.columns]
#vacant_data["street_address"] = vacant_data["address_street_number"].map(str) + " " + vacant_data["address_street_direction"] + " " + vacant_data["address_street_name"] + " " + vacant_data["address_street_suffix"]
#print(vacant_data)

#vacant_data_2017 = vacant_data[(vacant_data['DATE SERVICE REQUEST WAS RECEIVED'] > '2017-01-01') & (vacant_data['DATE SERVICE REQUEST WAS RECEIVED'] > '2017-12-31')]



#print(all_data, "WEEE")