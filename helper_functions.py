import pandas as pd

# Gets data from NY times and does some prep work
def retrieve_data():
    # Read current state and county data from NY times
    state_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv",
    )
    state_df = state_df.convert_dtypes()
    state_df.date = pd.to_datetime(state_df.date)

    county_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv",
    )
    county_df = county_df.convert_dtypes()
    county_df.date = pd.to_datetime(county_df.date)

    # Reindex and sort
    state_df = state_df.set_index(['state', 'date']).sort_index()
    county_df = county_df.set_index(['state', 'county', 'date']).sort_index()
    county_df.index = [county_df.index.map('{0[0]} - {0[1]}'.format), county_df.index.get_level_values(2)]

    # Get US totals up to latest date from which we have data from all states
    latest_date = state_df.reset_index(level=1).groupby(level=0).date.max().min()
    us_df = state_df.groupby(level=1).sum()
    us_df = us_df.loc[:latest_date]

    # Append US totals to state data
    us_df = pd.concat([us_df], keys=['USA'], names=['state'])
    us_df.fips = pd.NaT
    state_df = state_df.append(us_df)

    return state_df, county_df

if __name__=='__main__':
    retrieve_data()
