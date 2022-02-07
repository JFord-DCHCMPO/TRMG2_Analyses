import os
import pandas as pd
import caliper, caliperpy, traceback, sys
import numpy as np
import pandas as pd
from siuba import *
from plotnine import ggplot, aes, geom_line


##TRMG2

path = "c:/Users/JacobFo/TRMG2_v0.2/scenarios/base_2016/output/networks/scenario_links.bin"
hwy_2016_g2 = dk.GetDataFrameFromBin(path)

hwy_2016_g2['Total_Transit_Flow'] = hwy_2016_g2['AB_Total_TransitFlow'] + hwy_2016_g2['BA_Total_TransitFlow']

##Load TRMv6.2

path = "c:/Users/JacobFo/OneDrive - City of Durham/Full Model Runs/Original TRMv6.2_2016 - Copy/"
inpFname =  os.path.join(path, "Input/Highway/Highway_Line.bin")
hwy_2016_v6 = dk.GetDataFrameFromBin(inpFname)

replace_nas = hwy_2016_v6

replace_nas.fillna(value = 0,inplace = True)

replace_nas['TotVMT'] = replace_nas['ABAMVMT']+replace_nas['ABMDVMT']+replace_nas['ABNTVMT']+replace_nas['ABPMVMT']+replace_nas['BAAMVMT']+replace_nas['BAMDVMT']+replace_nas['BANTVMT']+replace_nas['BAPMVMT']

replace_nas['TotVHT'] = replace_nas['ABAMVHT']+replace_nas['ABMDVHT']+replace_nas['ABNTVHT']+replace_nas['ABPMVHT']+replace_nas['BAAMVHT']+replace_nas['BAMDVHT']+replace_nas['BANTVHT']+replace_nas['BAPMVHT']




pd.set_option('display.float_format', lambda x: '%.3f' % x)

WGS84 = "EPSG:4326"
CA_StatePlane = "EPSG:2229" # units are in feet
CA_NAD83Albers = "EPSG:3310" # units are in meters

SQ_MI_PER_SQ_M = 3.86 * 10**-7

def aggregate_by_geography(df, group_cols, 
                       sum_cols = [], mean_cols = [], 
                       count_cols = [], nunique_cols = []):

    final_df = df[group_cols].drop_duplicates().reset_index()
    
    def aggregate_and_merge(df, final_df, 
                            group_cols, agg_cols, AGGREGATE_FUNCTION):
        
        agg_df = df.pivot_table(index=group_cols,
                       values=agg_cols,
                       aggfunc=AGGREGATE_FUNCTION).reset_index()
        
        final_df = pd.merge(final_df, agg_df, 
                           on=group_cols, how="left", validate="1:1")
        return final_df

    
    if len(sum_cols) > 0:
        final_df = aggregate_and_merge(df, final_df, group_cols, sum_cols, "sum")
        
    if len(mean_cols) > 0:
        final_df = aggregate_and_merge(df, final_df, group_cols, mean_cols, "mean")
        
    if len(count_cols) > 0:
        final_df = aggregate_and_merge(df, final_df, group_cols, count_cols, "count")
 
    if len(nunique_cols) > 0:
        final_df = aggregate_and_merge(df, final_df, group_cols, nunique_cols, "nunique")
     
    return final_df.drop(columns = "index")


def attach_geometry(df, geometry_df, 
                    merge_col = ["Tract"], join="left"):

    gdf = pd.merge(
        geometry_df.to_crs(WGS84),
        df,
        on = merge_col,
        how = join,
    )
    
    return gdf
