import asyncio
import queue
from typing import TypedDict

import dash
import plotly.graph_objects as go
from dash import Input, Output, dcc, html


class GraphCoordinate(TypedDict):
    x: float
    y: float


data_queue: queue.Queue[GraphCoordinate] = queue.Queue()


def _run_dash():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.H2("Live Device Location Tracking"),
            html.Div(id="live-status-text"),
            dcc.Graph(id="live-map", style={"height": "75vh"}),
            dcc.Interval(id="map-interval", interval=500, n_intervals=0),
        ]
    )

    latest_data = {"x": [], "y": []}

    @app.callback(
        [Output("live-map", "figure"), Output("live-status-text", "children")],
        [Input("map-interval", "n_intervals")],
    )  # pyright: ignore[reportAny]
    def update_graph(n):
        while not data_queue.empty():
            point = data_queue.get_nowait()
            latest_data["x"].append(point["x"])
            latest_data["y"].append(point["y"])

        fig = go.Figure(
            go.Scatter(
                x=[latest_data["x"][-1]],
                y=[latest_data["y"][-1]],
                mode="markers",
                marker={"size": 8, "color": "blue"},
                line={"width": 2},
            )
        )
        _ = fig.update_layout(
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            xaxis=dict(range=[-20, 20], fixedrange=True),
            yaxis=dict(range=[-20, 20], fixedrange=True),

            margin={"l": 40, "r": 40, "t": 20, "b": 40},
        )

        status_text = f"Total points tracked: {len(latest_data['x'])}"
        return fig, status_text

    app.run(debug=False, port=1234, use_reloader=False)


async def host_on_website():
    _ = asyncio.get_running_loop().run_in_executor(None, _run_dash)

    def update_location(data: GraphCoordinate) -> None:
        data_queue.put(data)

    return update_location
