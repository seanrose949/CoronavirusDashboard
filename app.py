import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from helper_functions import retrieve_data

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Get dataframes from NY times
state_df, county_df = retrieve_data()

# Get list of states and counties for dropdowns
list_of_states = list(state_df.index.levels[0])
list_of_counties = list(county_df.index.levels[0])

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("UW-logo.png")
                        ),
                        html.H2("NY TIMES CORONAVIRUS DATA VISUALIZATION"),
                        html.P(
                            """Select different states or counties/regions
                            using the dropdowns. USA total can be selected from the state dropdown."""
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for selection of states
                                        dcc.Dropdown(
                                            id="state-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_states
                                            ],
                                            multi=True,
                                            placeholder="Select states",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for selection of state-county
                                        dcc.Dropdown(
                                            id="county-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_counties
                                            ],
                                            multi=True,
                                            placeholder="Select counties",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # html.P(id="total-us-cases"),
                        # html.P(id="total-state-selection"),
                        # html.P(id="total-county-selection"),
                        # html.P(id="date-value"),
                        dcc.Markdown(
                            children=[
                                "Source: [NY Times](https://github.com/nytimes/covid-19-data)\n",
                                "To be used for personal use only\n",
                                "Created using [dash](https://dash.plotly.com/)\n",
                                "[Source code available here](https://github.com/seanrose949/CoronavirusDashboard)"
                            ],
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="time-graph"),
                        # html.Div(
                        #     className="text-padding",
                        #     children=[
                        #         "Select state curve to see histogram by county."
                        #     ],
                        # ),
                        # dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)


# Pulls case and death time series for selected states and counties
def get_time_series(selected_data, df, default):
    # Check if anything is selected
    if selected_data is None or len(selected_data) is 0:
        selected_df = df.loc[[default]]
        selected_df.index = selected_df.index.remove_unused_levels()
    else:
        selected_df = df.loc[selected_data]
        selected_df.index = selected_df.index.remove_unused_levels()
    return selected_df


# Update time-series graph based on state and county dropdowns
@app.callback(
    Output("time-graph", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("county-dropdown", "value")
    ],
)
def update_graph(selected_states, selected_counties):
    # Get data for selected states and counties
    selected_state_df = get_time_series(selected_states, state_df, None)
    selected_county_df = get_time_series(selected_counties, county_df, None)

    fig = go.Figure()

    # Add traces for each selected state
    for idx in list(selected_state_df.index.levels[0]):
        case_bool = selected_state_df.loc[idx].cases > 0
        death_bool = selected_state_df.loc[idx].deaths > 0
        fig.add_trace(
            go.Scatter(
                x=selected_state_df.loc[idx].index[case_bool],
                y=selected_state_df.loc[idx].cases[case_bool],
                mode='lines+markers',
                name=idx + ' Cases'
            )
        )
        fig.add_trace(
            go.Scatter(
                x=selected_state_df.loc[idx].index[death_bool],
                y=selected_state_df.loc[idx].deaths[death_bool],
                mode='lines+markers',
                name=idx + ' Deaths'
            )
        )

    # Add traces for each selected county
    for idx in list(selected_county_df.index.levels[0]):
        case_bool = selected_county_df.loc[idx].cases > 0
        death_bool = selected_county_df.loc[idx].deaths > 0
        fig.add_trace(
            go.Scatter(
                x=selected_county_df.loc[idx].index[case_bool],
                y=selected_county_df.loc[idx].cases[case_bool],
                mode='lines+markers',
                name=idx + ' Cases'
            )
        )
        fig.add_trace(
            go.Scatter(
                x=selected_county_df.loc[idx].index[death_bool],
                y=selected_county_df.loc[idx].deaths[death_bool],
                mode='lines+markers',
                name=idx + ' Deaths'
            )
        )
    fig.update_layout(
        autosize=True,
        margin=go.layout.Margin(l=0, r=35, t=0, b=0),
        showlegend=True,
        yaxis=dict(type='log'),
        paper_bgcolor='#dbdbdb',
        plot_bgcolor='#dbdbdb'
    )

    return fig


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050, debug=False)
