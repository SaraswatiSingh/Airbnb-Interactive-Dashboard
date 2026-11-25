import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# ----------------------------------------------------
# 1. LOAD DATASET
# ----------------------------------------------------

url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"

df = pd.read_csv(url)

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())


# ----------------------------------------------------
# 2. CLEAN DATASET
# ----------------------------------------------------

required_columns = [
    'latitude',
    'longitude',
    'price',
    'minimum_nights'
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")


# Convert columns into numeric values

for col in required_columns:

    if col == 'price':

        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(
                r'[^\d.]', '', regex=True
            ),
            errors='coerce'
        )

    else:

        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )


# Remove missing values

df = df.dropna(subset=required_columns)


# Remove invalid geographical coordinates

df = df[
    df['latitude'].between(-90, 90) &
    df['longitude'].between(-180, 180)
]


print("Clean dataset:", df.shape)
print(df.head())


if df.empty:
    raise ValueError("No valid records found in dataset.")


# Calculate maximum price

max_price = max(1000, int(df['price'].max()))


# ----------------------------------------------------
# 3. CREATE DASH APP
# ----------------------------------------------------

app = Dash(__name__)
server = app.server


app.layout = html.Div([

    html.H1(
        'Airbnb Listings - Monterrey',
        style={
            'textAlign': 'center',
            'color': '#333'
        }
    ),

    html.H3("Select Minimum Nights"),

    dcc.Slider(
        id='night-slider',
        min=1,
        max=30,
        step=1,
        value=3,
        marks={
            n: str(n)
            for n in range(1, 31, 5)
        }
    ),

    html.Br(),

    html.H3("Select Price Range"),

    dcc.RangeSlider(
        id='price-slider',
        min=0,
        max=max_price,
        value=[0, min(2500, max_price)],
        step=100,
        marks=None,
        tooltip={
            'placement': 'bottom',
            'always_visible': True
        }
    ),

    html.Br(),

    html.Div(
        id='count',
        style={
            'fontWeight': 'bold',
            'fontSize': '18px',
            'marginBottom': '15px'
        }
    ),

    dcc.Graph(
        id='airbnb-map',
        style={
            'height': '700px'
        }
    )

], style={'padding': '30px'})


# ----------------------------------------------------
# 4. CALLBACK FUNCTION
# ----------------------------------------------------

@app.callback(

    Output('airbnb-map', 'figure'),

    Output('count', 'children'),

    Input('night-slider', 'value'),

    Input('price-slider', 'value')

)


def update_graph(nights, price_range):

    # Filter dataset

    dff = df[

        (df['minimum_nights'] >= nights) &

        (df['price'] >= price_range[0]) &

        (df['price'] <= price_range[1])

    ]


    print("Filtered rows:", len(dff))


    # Create scatter plot

    fig = px.scatter(

        dff,

        x='longitude',

        y='latitude',

        color='price',

        hover_data=[
            'price',
            'minimum_nights'
        ],

        title='Airbnb Listings Scatter Plot',

        labels={
            'longitude': 'Longitude',
            'latitude': 'Latitude',
            'price': 'Price'
        }

    )


    # Update graph layout

    fig.update_layout(

        height=700,

        template='plotly_white',

        xaxis_title='Longitude',

        yaxis_title='Latitude'

    )


    # Display total listings

    count_text = f"Total Listings Found: {len(dff)}"


    return fig, count_text


# ----------------------------------------------------
# 5. RUN APPLICATION
# ----------------------------------------------------

if __name__ == '__main__':

    app.run(debug=True)
