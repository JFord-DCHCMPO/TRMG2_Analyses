import os
import pandas as pd
from siuba import *

WGS84 = "EPSG:4326"

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
