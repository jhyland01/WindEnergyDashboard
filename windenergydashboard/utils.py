import pandas as pd
import altair as alt


def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    return (
        alt.Chart(input_df)
        .mark_rect()
        .encode(
            y=alt.Y(
                f"{input_y}:O",
                axis=alt.Axis(
                    title="Date",
                    titleFontSize=18,
                    titlePadding=15,
                    titleFontWeight=900,
                    labelAngle=0,
                    labelExpr="timeFormat(datum.value, '%Y-%m-%d')",
                ),
            ),
            x=alt.X(
                f"{input_x}:O",
                axis=alt.Axis(
                    title="",
                    titleFontSize=18,
                    titlePadding=15,
                    titleFontWeight=900,
                ),
            ),
            color=alt.Color(
                f"{input_color}:Q",
                legend=alt.Legend(
                    title="Power (kW)",
                    orient="bottom",
                    offset=0,
                ),
                scale=alt.Scale(scheme=input_color_theme),
            ),
            stroke=alt.value("black"),
            strokeWidth=alt.value(0.25),
        )
        .properties(width=500)
        .configure_axis(labelFontSize=12, titleFontSize=12)
    )


def make_donut(input_response, input_text, input_color):
    if input_color == "blue":
        chart_color = ["#29b5e8", "#155F7A"]
    if input_color == "green":
        chart_color = ["#27AE60", "#12783D"]
    if input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    if input_color == "red":
        chart_color = ["#E74C3C", "#781F16"]

    source = pd.DataFrame(
        {"Topic": ["", input_text], "% value": [100 - input_response, input_response]}
    )
    source_bg = pd.DataFrame({"Topic": ["", input_text], "% value": [100, 0]})

    plot = (
        alt.Chart(source)
        .mark_arc(innerRadius=45, cornerRadius=25)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    # range=['#29b5e8', '#155F7A']),  # 31333F
                    range=chart_color,
                ),
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )

    text = plot.mark_text(
        align="center",
        color="#29b5e8",
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic",
    ).encode(text=alt.value(f"{input_response} %"))
    plot_bg = (
        alt.Chart(source_bg)
        .mark_arc(innerRadius=45, cornerRadius=20)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    range=chart_color,
                ),  # 31333F
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )
    return plot_bg + plot + text
