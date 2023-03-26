import pandas as pd
import numpy as np
import openpyxl


class DataModel():

    def __init__(self):
        pass

    def score_calc(self, mergedRes, community_crime_statistic_df, monthly_economic_indicator_df, unemployment_rate_df,
                   community, year):
        weights = {
            'Assault (Non-domestic)': 0.2,
            'Theft FROM Vehicle': 0.05,
            'Violence Other (Non-domestic)': 0.05,
            'Theft OF Vehicle': 0.1,
            'Break & Enter - Commercial': 0.1,
            'Break & Enter - Other Premises': 0.05,
            'Break & Enter - Dwelling': 0.15,
            'Street Robbery': 0.15,
            'Commercial Robbery': 0.05
        }

        rslt_df = mergedRes[mergedRes['Date'].str.contains(year)]
        community_df = rslt_df[rslt_df['Community Name'] == community]
        total_cat = {}
        for x in weights:
            cat_df = rslt_df[rslt_df['Category'] == x]
            num_df = community_df[community_df['Category'] == x]
            num = int(num_df['Crime Count'].sum()) / int(cat_df['Crime Count'].sum())
            total_cat[x] = num

        score = 0

        for x in weights:
            score = score + weights[x] * total_cat[x]

        unique_df = community_crime_statistic_df.copy()
        unique_df = unique_df.drop(
            columns=['Sector', 'Category', 'Crime Count', 'Date'])
        unique_df = unique_df.drop_duplicates().fillna(0)

        denominator = unique_df['Resident Count'].sum()

        community_df = unique_df[unique_df['Community Name'] == community]
        numerator = community_df['Resident Count'].sum()

        score = score + int(numerator) / int(denominator) * 0.1

        return {"Score": score, "CenterPoint": community_df['Community Center Point'].loc[community_df.index[0]],
                "Polygon": community_df['Multipolygon'].loc[community_df.index[0]]}

    def gen_csv(self):
        community_name = []
        year_list = []
        score = []
        normscore = []
        center_point = []
        polygon = []
        community_crime_statistic_df = pd.read_csv(
            "https://data.calgary.ca/api/views/78gh-n26t/rows.csv?accessType=DOWNLOAD")
        monthly_economic_indicator_df = pd.read_csv(
            "https://data.calgary.ca/api/views/7cvb-8ame/rows.csv?accessType=DOWNLOAD")
        unemployment_rate_df = pd.read_csv("https://data.calgary.ca/api/views/vxxi-pm4v/rows.csv?accessType=DOWNLOAD")
        communities = community_crime_statistic_df['Community Name'].unique()
        years = community_crime_statistic_df['Year'].unique()
        community_crime_statistic_df.drop(["Year", "Month", "ID"], axis=1, inplace=True)
        monthly_economic_indicator_df["Date"] = monthly_economic_indicator_df["Date"].str[:-3]
        mergedRes = pd.merge(community_crime_statistic_df, monthly_economic_indicator_df, on='Date', how="left")
        for community in communities:
            for year in years:
                temp = self.score_calc(mergedRes, community_crime_statistic_df, monthly_economic_indicator_df,
                                       unemployment_rate_df, community, str(year))
                year_list.append(year)
                community_name.append(community)
                score.append(temp["Score"])
                center_point.append(temp["CenterPoint"])
                polygon.append(temp["Polygon"])
                print(f"Processing {community} {year}")
        for idx, x in enumerate(score):
            print(f"score before: {score[idx]}")
            normscore.append(((x - min(score)) / (max(score) - min(score))) * 5)
            # score[idx] = ((x-min(score))/(max(score)-min(score)))*5

        dict = {
            "Community Name": community_name,
            "Year": year_list,
            "Normalized Score": normscore,
            "Score": score,
            "Center Point": center_point,
            "Polygon": polygon
        }

        df = pd.DataFrame(dict)
        # df["Score"] = ((df["Score"]-df["Score"].min())/(df["Score"].max()-df["Score"].min()))*5
        print(df)
        df.to_excel("./static/output.xlsx")
