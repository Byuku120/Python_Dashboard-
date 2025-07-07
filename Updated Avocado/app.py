import pandas as pd
from dash import Dash, Input, Output, dcc, html

# Load dataset
df = pd.read_csv("assets/avocado.csv")
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
df = df.sort_values("Date")
df["Year"] = df["Date"].dt.year

# Dropdown options
unique_regions = df["region"].sort_values().unique()
unique_types = df["type"].sort_values().unique()

# External stylesheets for nice fonts
external_stylesheets = [{
    "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet",
}]

# Initialize app
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.P("🥑", className="header-emoji"),
        html.H1("Avocado Analytics", className="header-title"),
        html.P(
            "Analyze the behavior of avocado prices and sales volume in the US from 2015 to 2018.",
            className="header-description",
        ),
    ], className="header"),

    # Filters
    html.Div([
        html.Div([
            html.Div("Region", className="menu-title"),
            dcc.Dropdown(
                id="region-filter",
                options=[{"label": region, "value": region} for region in unique_regions],
                value="Albany",
                clearable=False,
                className="dropdown",
            ),
        ]),
        html.Div([
            html.Div("Type", className="menu-title"),
            dcc.Dropdown(
                id="type-filter",
                options=[{"label": t.title(), "value": t} for t in unique_types],
                value="organic",
                clearable=False,
                className="dropdown",
            ),
        ]),
        html.Div([
            html.Div("Date Range", className="menu-title"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=df["Date"].min().date(),
                max_date_allowed=df["Date"].max().date(),
                start_date=df["Date"].min().date(),
                end_date=df["Date"].max().date(),
            ),
        ]),
    ], className="menu"),

    # Graphs section
    html.Div([
        html.Div(dcc.Graph(id="price-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="volume-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="top-region-chart", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="price-by-type", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="volume-by-year", config={"displayModeBar": False}), className="card"),
        html.Div(dcc.Graph(id="bags-vs-price", config={"displayModeBar": False}), className="card"),
    ], className="wrapper"),
])

# Callback to update all charts based on filters
@app.callback(
    Output("price-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("top-region-chart", "figure"),
    Output("price-by-type", "figure"),
    Output("volume-by-year", "figure"),
    Output("bags-vs-price", "figure"),
    Input("region-filter", "value"),
    Input("type-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_graphs(selected_region, selected_type, start_date, end_date):
    filtered_df = df.query(
        "region == @selected_region and type == @selected_type and Date >= @start_date and Date <= @end_date"
    )

    # Line chart: Average Price over time
    price_chart = {
        "data": [{
            "x": filtered_df["Date"],
            "y": filtered_df["AveragePrice"],
            "type": "lines",
            "hovertemplate": "$%{y:.2f}<extra></extra>",
        }],
        "layout": {
            "title": {"text": "Average Price of Avocados", "x": 0.05},
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#407E60B8"],
        },
    }

    # Line chart: Volume over time
    volume_chart = {
        "data": [{
            "x": filtered_df["Date"],
            "y": filtered_df["Total Volume"],
            "type": "lines",
        }],
        "layout": {
            "title": {"text": "Avocados Sold", "x": 0.05},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#73CE99"],
        },
    }

    # Bar chart: Top 10 regions by volume
    top_10_regions = (
        df.query("type == @selected_type and Date >= @start_date and Date <= @end_date")
        .groupby("region", as_index=False)["Total Volume"]
        .sum()
        .sort_values("Total Volume", ascending=False)
        .head(10)
    )
    top_region_chart = {
        "data": [{
            "type": "bar",
            "x": top_10_regions["Total Volume"],
            "y": top_10_regions["region"],
            "orientation": "h",
            "text": top_10_regions["Total Volume"].round(0),
            "textposition": "auto",
            "marker": {"color": "#80C09AD5"},
        }],
        "layout": {
            "title": {"text": "Top 10 Regions by Avocados Sold", "x": 0.05},
            "xaxis": {"title": "Total Volume"},
            "yaxis": {"title": "Region", "autorange": "reversed"},
            "height": 500,
            "margin": {"l": 100, "r": 20, "t": 50, "b": 50},
        },
    }

    # Bar chart: Average Price by Type
    avg_price_by_type = (
        df.query("region == @selected_region and Date >= @start_date and Date <= @end_date")
        .groupby("type", as_index=False)["AveragePrice"]
        .mean()
    )
    price_by_type_chart = {
        "data": [{
            "type": "bar",
            "x": avg_price_by_type["type"],
            "y": avg_price_by_type["AveragePrice"],
            "marker": {"color": ["#AEEAC4EA", "#08843ED6"]},
        }],
        "layout": {
            "title": {"text": "Average Price by Avocado Type", "x": 0.05},
            "yaxis": {"tickprefix": "$"},
        },
    }

    # Bar chart: Volume per year
    yearly_volume = (
        df.query("region == @selected_region and type == @selected_type and Date >= @start_date and Date <= @end_date")
        .groupby("Year", as_index=False)["Total Volume"]
        .sum()
    )
    volume_by_year_chart = {
        "data": [{
            "type": "bar",
            "x": yearly_volume["Year"].astype(str),
            "y": yearly_volume["Total Volume"],
            "marker": {"color": "#2A87468A"},
        }],
        "layout": {
            "title": {"text": "Total Volume by Year", "x": 0.05},
            "xaxis": {"title": "Year"},
            "yaxis": {"title": "Volume"},
        },
    }

    # Extra (but missing): scatter chart placeholder
    scatter_placeholder = {
        "data": [],
        "layout": {
            "title": {"text": "Bags vs Price (Placeholder)", "x": 0.05}
        }
    }

    return (
        price_chart,
        volume_chart,
        top_region_chart,
        price_by_type_chart,
        volume_by_year_chart,
        scatter_placeholder,
    )

# Run app
if __name__ == "__main__":
    app.run(debug=True)


