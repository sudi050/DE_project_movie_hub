from flask import Flask, session 
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from config_external_data import Genre_List, actor_high_rated_movie_df_cols
from navbar import create_navbar

def create_dash_app(server, get_db):
    dash_app = dash.Dash(__name__, server=server, url_base_pathname="/dash/", external_stylesheets=['/static/css/dash.css'])
    import plotly.graph_objs as go

    def create_bar_chart(data, title, x_title, y_title):
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data.iloc[:, 0],  # Names
                    y=data.iloc[:, 1],  # Counts/Values
                    text=data.iloc[:, 1],  # Data labels
                    textposition="auto",  # Show data labels on the bars
                    marker_color="deeppink",  # Custom color for bars
                    marker_line_color="black",  # Outline color for bars
                    marker_line_width=2,  # Width of bar outlines
                )
            ]
        )

        fig.update_layout(
            title={
                "text": title,
                "x": 0.5, 
                "xanchor": "center",
                "font": {"size": 40, "family": "Arial", "color": "black"},
            },
            xaxis={
                "title": x_title,
                "tickangle": -45, 
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": False, 
            },
            yaxis={
                "title": y_title,
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True,  
                "gridcolor": "lightgrey",  
            },
            plot_bgcolor="white",
        )

        return dcc.Graph(figure=fig)

    def create_collaboration_bar_chart(data, title):
        data["collaboration"] = (
            data["director_name"]
            + " & "
            + data["actor_name"]
            + " - "
            + data["original_title"]
        )

        fig = go.Figure(
            data=[
                go.Bar(
                    x=data["revenue"],
                    y=data["collaboration"],
                    orientation="h",
                    text=data["revenue"],  
                    textposition="auto",
                    marker_color="deeppink",
                    marker_line_width=2,
                )
            ]
        )

        fig.update_layout(
            title={
                "text": title,
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 40, "color": "black"},
            },
            xaxis={
                "title": "Revenue",
                "title_font": {"size": 15, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
            },
            yaxis={
                "title": "Director & Actor Collaboration",
                "title_font": {"size": 15, "family": "Arial"},
                "tickfont": {"size": 10, "family": "Arial"},
            },
            plot_bgcolor="white",
        )

        return dcc.Graph(figure=fig)


    import statsmodels.api as sm
    import plotly.express as px
    import plotly.graph_objects as go

    def create_popularity_revenue_scatter(data, correlation):
        fig = px.scatter(
            data,
            x="average_popularity",
            y="average_revenue",
            color="genre_name",
            labels={
                "average_popularity": "Average Popularity",
                "average_revenue": "Average Revenue",
                "genre_name": "Genre",
            },)

        X = data["average_popularity"]
        X = sm.add_constant(X)  
        y = data["average_revenue"]
        model = sm.OLS(y, X).fit()
        trendline = model.predict(X)

        fig.add_trace(
            go.Scatter(
                x=data["average_popularity"],
                y=trendline,
                mode="lines",
                line=dict(color="black"),
                name="Trendline",
            ))

        fig.update_layout(
            title={
                "text": f"Correlation between Average Popularity and Average Revenue by Genre (r = {correlation:.2f})",
                "x": 0.5, 
                "xanchor": "center",
                "font": {"size": 25, "family": "Arial", "color": "black"},
            },
            xaxis={
                "title": "Average Popularity",
                "tickangle": -45, 
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True, 
            },
            yaxis={
                "title": "Average Revenue",
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True,  
                "gridcolor": "lightgrey",
            },
            legend_title_text="Genres",
            plot_bgcolor="white",
        )
        return dcc.Graph(figure=fig)

    def create_genre_rating_bar_plot(data, genre1, genre2):
        df = pd.DataFrame(
            data,
            columns=[
                "actor_name",
                f"average_{genre1.lower()}_rating",
                f"average_{genre2.lower()}_rating",
                "rating_difference",
            ],
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["actor_name"],
                y=df[f"average_{genre1.lower()}_rating"],
                name=f"Average {genre1} Rating",
                marker_color="blue",
                text=df[f"average_{genre1.lower()}_rating"].apply(lambda x: round(x, 4)),
                textposition="outside",
            )
        )

        fig.add_trace(
            go.Bar(
                x=df["actor_name"],
                y=df[f"average_{genre2.lower()}_rating"],
                name=f"Average {genre2} Rating",
                marker_color="orange",
                text=df[f"average_{genre2.lower()}_rating"].apply(lambda x: round(x, 4)),
                textposition="outside",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["actor_name"],
                y=df["rating_difference"],
                mode="lines+markers+text",
                name="Rating Difference",
                line=dict(color="green", width=2),
                marker=dict(color="green", size=8),
                text=df["rating_difference"].apply(lambda x: round(x, 2)),
                textposition="top center",
            )
        )

        fig.update_layout(
            title={
                "text": f"Average Ratings in {genre1} vs. {genre2} for Top {len(df)} Actors by Rating Difference",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 30, "family": "Arial", "color": "black"},
            },
            xaxis={
                "title": "Actor",
                "tickangle": -45,
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": False,
            },
            yaxis={
                "title": "Average Rating",
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True,
                "gridcolor": "lightgrey",
            },
            barmode="group",
            plot_bgcolor="white",
            legend_title_text="Genre",
        )

        return dcc.Graph(figure=fig)

    def create_prod_house_revenue_chart(df):
        df_sorted = df.sort_values(by="total_revenue", ascending=False).head(len(df))
        df_sorted["prod_genre_combination"] = (
            df_sorted["production_company_name"] + " - " + df_sorted["genre_name"]
        )
        genres = df_sorted["genre_name"].unique()
        color_map = {
            genre: f"rgb({(i * 50) % 255}, {(i * 100) % 255}, {(i * 150) % 255})"
            for i, genre in enumerate(genres)
        }
        df_sorted["color"] = df_sorted["genre_name"].map(color_map)
        df_sorted["formatted_revenue"] = df_sorted["total_revenue"].apply(
            lambda x: f"{float(x) / 1e9:.2f}B")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df_sorted["prod_genre_combination"], 
                y=df_sorted["total_revenue"],
                marker=dict(color=df_sorted["color"]),
                text=df_sorted.apply(
                    lambda row: f"{row['genre_name']}<br>{row['formatted_revenue']}<br>{row['total_revenue']}",
                    axis=1,
                ),
                textposition="inside", 
                hoverinfo="text",
            )
        )

        fig.update_layout(
            title={
                "text": f"Top {len(df)} Production Companies by Total Revenue",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 40, "family": "Arial", "color": "black"},
            },
            xaxis={
                "title": "Production Company - Genre",
                "tickangle": -45,  
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": False, 
            },
            yaxis={
                "title": "Total Revenue",
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True,
                "gridcolor": "lightgrey", 
            },
            plot_bgcolor="white",
            showlegend=False, 
        )

        return dcc.Graph(figure=fig)

    def create_high_rated_actors_chart(data,genre,flag=0):
        """
        Generates a grouped bar chart showing actor appearances in high-rated movies across genres.
        """
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["above_9_count"],
                name="Above 9",
                marker_color="purple",
            ))
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["above_8_count"],
                name="Above 8",
                marker_color="blue",
            ))
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["above_7_count"],
                name="Above 7",
                marker_color="green",
            ))
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["above_6_count"],
                name="Above 6",
                marker_color="orange",
            ))
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["above_5_count"],
                name="Above 5",
                marker_color="pink",
            ))
        fig.add_trace(
            go.Bar(
                x=data["actor_name"] + " (" + data["genre_name"] + ")",
                y=data["below_5_count"],
                name="Below 5",
                marker_color="red",
            ))
        
        if flag == 0:
            title = f"Top {len(data)} Actors Appearances in High-Rated Movies"
        else:
            title = f"Top {len(data)} Actors Appearances in High-Rated {genre} Movies"
        fig.update_layout(
            barmode="group",
            title={
                "text": f"{title}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 40},
            },
            xaxis_title="Actor (Genre)",
            yaxis_title="Appearance Count",
            xaxis=dict(tickangle=-45),
            plot_bgcolor="white",
            legend_title="Rating Category",
            legend=dict(
                orientation="h", yanchor="top", y=1.15, xanchor="center", x=0.5
            ),)

        return dcc.Graph(figure=fig)

    def create_genre_profitability_chart(df):
        df_sorted = df.sort_values(by="average_profit_margin", ascending=False)
        genres = df_sorted["genre_name"].unique()
        color_map = {
            genre: f"rgb({(i * 60) % 255}, {(i * 120) % 255}, {(i * 180) % 255})"
            for i, genre in enumerate(genres)
        }
        df_sorted["color"] = df_sorted["genre_name"].map(color_map)
        df_sorted["formatted_profit_margin"] = df_sorted["average_profit_margin"].apply(
            lambda x: f"{x:.2f}"
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df_sorted["genre_name"],
                y=df_sorted["average_profit_margin"],
                marker=dict(color=df_sorted["color"]), 
                text=df_sorted.apply(
                    lambda row: f"{row['movie_count']} Movies<br>Avg Profit Margin: {row['formatted_profit_margin']}",
                    axis=1,
                ),
                textposition="inside",
                hoverinfo="text",
            )
        )

        fig.update_layout(
            title={
                "text": "Most Profitable Prequels and Sequels by Genre",
                "x": 0.5,  
                "xanchor": "center",
                "font": {"size": 30, "family": "Arial", "color": "black"},
            },
            xaxis={
                "title": "Genre",
                "tickangle": -45,  
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": False,  
            },
            yaxis={
                "title": "Average Profit Margin",
                "title_font": {"size": 20, "family": "Arial"},
                "tickfont": {"size": 12, "family": "Arial"},
                "showgrid": True,  # Show horizontal grid lines
                "gridcolor": "lightgrey",  # Custom grid line color
                # "tickvals": [1, 10, 50, 100, 200, 500, 1000, 2000, 3000, 4000, 5000],
            },
            plot_bgcolor="white",
            showlegend=False,  
        )

        return dcc.Graph(figure=fig)

    def get_query_results(db, query, limit):
        """
        Database query function to fetch results and return as a DataFrame.
        """
        cursor = db.cursor()
        query = query.format(limit=limit)
        cursor.execute(query)
        results = cursor.fetchall()
        return pd.DataFrame(results)

    def get_top_collaborations(db, limit):
        query = f"""
        WITH highest_grossing_movies AS (
            SELECT id AS movie_id, original_title, revenue
            FROM movies
            WHERE revenue IS NOT NULL
            ORDER BY revenue DESC
        )

        SELECT d."Name" AS director_name,
            a."Name" AS actor_name,
            COUNT(*) AS total_collaborations,
            hgm.original_title,
            hgm.revenue
        FROM highest_grossing_movies AS hgm, movie_directors AS md,
            directors AS d, movie_actors AS ma, actors AS a
        WHERE hgm.movie_id = md.movie_id 
        AND md.director_id = d."ID"
        AND hgm.movie_id = ma.movie_id 
        AND ma.actor_id = a."ID"
        GROUP BY d."Name", a."Name", hgm.original_title, hgm.revenue
        ORDER BY hgm.revenue DESC, director_name, actor_name
        LIMIT {limit};
        """
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(
            rows,
            columns=[
                "director_name",
                "actor_name",
                "total_collaborations",
                "original_title",
                "revenue",
            ],
        )

    def fetch_top_actors_by_genre_difference(
        db, limit=5, genre1="Drama", genre2="Comedy"
    ):
        query = f"""
        SELECT a."Name" AS actor_name,
            COALESCE(AVG(CASE WHEN g."Name" = '{genre1}' THEN m.vote_average END), 0) AS average_{genre1.lower()}_rating,
            COALESCE(AVG(CASE WHEN g."Name" = '{genre2}' THEN m.vote_average END), 0) AS average_{genre2.lower()}_rating,
            ABS(COALESCE(AVG(CASE WHEN g."Name" = '{genre1}' THEN m.vote_average END), 0) - 
                    COALESCE(AVG(CASE WHEN g."Name" = '{genre2}' THEN m.vote_average END), 0)) AS rating_difference
        FROM actors AS a, movie_actors AS ma, movies AS m, genres AS g, movie_genres AS mg
        WHERE a."ID" = ma.actor_id 
        AND ma.movie_id = m.id 
        AND m.id = mg.movie_id 
        AND mg.genre_id = g."ID"
        GROUP BY a."Name"
        HAVING COUNT(DISTINCT CASE WHEN g."Name" = '{genre1}' THEN g."ID" END) > 0
        AND COUNT(DISTINCT CASE WHEN g."Name" = '{genre2}' THEN g."ID" END) > 0
        ORDER BY rating_difference DESC
        LIMIT {limit};
        """

        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def render_dashboard(
        option = 1,
        entity_type=None,
        limit=None,
        limit_movies=None,
        name_genre_actors_vote=None,
        limit_sci_fi_actors=None,
        limit_collaborations=None,
        name_compare_genre1=None,
        name_compare_genre2=None,
        limit_actors_ratings=None,
        limit_prod_comp_value=None,
        name_prod_comp_genre=None,
        limit_prod_comp_genre_value=None,
        name_genre_movie_vote=None
    ):
        # if "user_id" not in session:
        #     return html.Div([
        #             html.H1("Please sign in to access this page."),
        #             html.A("Sign In", href="/"),
        #         ])

        db = get_db()

        if option == 1:
            if entity_type == "actors":
                t1 = "actors"
                id1 = "actor"
            elif entity_type == "directors":
                t1 = "directors"
                id1 = "director"
            else:
                t1 = "prod_companies"
                id1 = "movie"

            query = f"""
            SELECT d."Name", COUNT(md.movie_id) AS movie_count
            FROM {t1} AS d
            JOIN movie_{t1} AS md ON d."ID" = md.{id1}_id
            WHERE d."Name" != 'N/A'
            GROUP BY d."Name"
            ORDER BY movie_count DESC
            LIMIT {limit};
            """
            data = get_query_results(db, query, limit)
            contributor_bar_chart = create_bar_chart(
                data,
                f"Top {limit} {entity_type} by Movie Count",
                "Director",
                "Movie Count",
            )
            return html.Div([contributor_bar_chart])

        if option == 2:
            query_profit_margin = f"""
            SELECT original_title, (revenue / budget) AS profit_margin
            FROM movies
            WHERE budget > 0 
            ORDER BY profit_margin DESC
            LIMIT {limit_movies};
            """
            profit_data = get_query_results(db, query_profit_margin, limit_movies)
            profit_margin_chart = create_bar_chart(
                profit_data,
                f"Top {limit_movies} Movies by Profit Margin",
                "Movie Title",
                "Profit Margin (Revenue/Budget)",
            )
            return html.Div([profit_margin_chart])

        if option == 3:
            if entity_type == "actors":
                t1 = "actors"
                t2 = "movie_actors"
                id2 = "actor_id"
            elif entity_type == "directors":
                t1 = "directors"
                t2 = "movie_directors"
                id2 = "director_id"
            else:
                t1 = "prod_companies"
                t2 = "movie_prod_companies"
                id2 = "prod_comp_id"
            
            query_top_directors = f"""
            SELECT a."Name", COUNT(m.id) AS movie_count
            FROM {t1} AS a
            JOIN {t2} AS ma ON a."ID" = ma.{id2}
            JOIN movies AS m ON ma.movie_id = m.id
            WHERE m.id IN (
                SELECT id
                FROM movies
                WHERE revenue IS NOT NULL
                ORDER BY revenue DESC
                LIMIT {limit_movies}
            )
            GROUP BY a."Name"
            ORDER BY movie_count DESC
            LIMIT {limit};
            """
            top_directors_data = get_query_results(
                db, query_top_directors, limit
            )
            top_directors_chart = create_bar_chart(
                top_directors_data,
                f"Top {limit} {entity_type} by High-Revenue Movie Count",
                "Director",
                "High-Revenue Movie Count",
            )
            return html.Div([top_directors_chart])

        if option == 4:
            query_top_sci_fi_actors = f"""
            SELECT a."Name" AS actor_name, AVG(m.vote_average) AS average_vote
            FROM actors AS a 
            JOIN movie_actors AS ma ON a."ID" = ma.actor_id
            JOIN movies AS m ON ma.movie_id = m.id
            JOIN movie_genres AS mg ON m.id = mg.movie_id
            JOIN genres AS g ON mg.genre_id = g."ID"
            WHERE g."Name" = '{name_genre_actors_vote}'
            GROUP BY a."Name"
            ORDER BY average_vote DESC
            LIMIT {limit_sci_fi_actors};
            """
            sci_fi_actors_data = get_query_results(
                db, query_top_sci_fi_actors, limit_sci_fi_actors
            )
            sci_fi_actors_chart = create_bar_chart(
                sci_fi_actors_data,
                f"Top {limit_sci_fi_actors} {name_genre_actors_vote} Actors by Average Vote",
                "Actor",
                "Average Vote",
            )
            return html.Div([sci_fi_actors_chart])

        if option == 5:
            collaboration_data = get_top_collaborations(db, limit_collaborations)
            collaboration_chart = create_collaboration_bar_chart(
                collaboration_data,
                f"Top {limit_collaborations} Director-Actor Collaborations by Revenue",
            )
            return html.Div([collaboration_chart])

        if option == 6:
            query = """
            SELECT g."Name" AS genre_name,
                AVG(m.popularity) AS average_popularity,
                AVG(m.revenue) AS average_revenue
            FROM movies AS m, movie_genres AS mg , genres AS g 
            WHERE m.id = mg.movie_id AND mg.genre_id = g."ID"
            AND m.revenue IS NOT NULL AND m.popularity IS NOT NULL
            GROUP BY g."Name"
            ORDER BY g."Name";
            """
            dir_actor_sql_df = pd.read_sql(query, db)
            correlation = dir_actor_sql_df["average_popularity"].corr(
                dir_actor_sql_df["average_revenue"]
            )
            correlation_chart = create_popularity_revenue_scatter(
                dir_actor_sql_df, correlation
            )
            return html.Div([correlation_chart])
        if option == 7:
            data = fetch_top_actors_by_genre_difference(
                db,
                limit=limit_actors_ratings,
                genre1=name_compare_genre1,
                genre2=name_compare_genre2,
            )
            genre_rating_bar_chart = create_genre_rating_bar_plot(
                data, genre1=name_compare_genre1, genre2=name_compare_genre2
            )
            return html.Div([genre_rating_bar_chart])

        if option == 8: 
            query_prd_house_revenue = f"""
            SELECT pc."Name" AS production_company_name, g."Name" AS genre_name, 
                SUM(m.revenue) AS total_revenue
            FROM prod_companies AS pc 
            JOIN movie_prod_companies AS mpc ON pc."ID" = mpc.prod_comp_id
            JOIN movies AS m ON mpc.movie_id = m.id
            JOIN movie_genres AS mg ON m.id = mg.movie_id
            JOIN genres AS g ON mg.genre_id = g."ID"
            WHERE m.revenue IS NOT NULL
            GROUP BY pc."Name", g."Name"
            ORDER BY total_revenue DESC
            LIMIT {limit_prod_comp_value};
            """

            prod_comp_sql_df = get_query_results(
                db, query_prd_house_revenue, limit_prod_comp_value
            )
            prod_comp_sql_df.columns = [
                "production_company_name",
                "genre_name",
                "total_revenue",
            ]
            prod_house_revenue_chart = create_prod_house_revenue_chart(prod_comp_sql_df)
            return html.Div([prod_house_revenue_chart])

        if option == 9:
            query_prd_house_genre_revenue = f"""
            SELECT pc."Name" AS production_company_name, SUM(m.revenue) AS total_revenue
            FROM prod_companies AS pc , movie_prod_companies AS mpc , movies AS m ,
            movie_genres AS mg , genres AS g
            WHERE pc."ID" = mpc.prod_comp_id AND  mpc.movie_id = m.id AND
            m.id = mg.movie_id AND mg.genre_id = g."ID" AND
            m.revenue IS NOT NULL AND g."Name" = '{name_prod_comp_genre}' 
            GROUP BY pc."Name"
            ORDER BY total_revenue DESC
            LIMIT {limit_prod_comp_genre_value};
            """

            prod_comp_genre_sql_df = get_query_results(
                db, query_prd_house_genre_revenue, limit_prod_comp_value
            )
            prod_comp_genre_sql_df.columns = [
                "production_company_name",
                "total_revenue",
            ]
            prod_house_genre_revenue_chart = create_bar_chart(
                prod_comp_genre_sql_df,
                f"Top {limit_prod_comp_genre_value} production Houses for the Genre {name_prod_comp_genre} by Revenue",
                "Production Houses",
                "Total Revenue",
            )
            return html.Div([prod_house_genre_revenue_chart])
        
        query_part1 = """SELECT a."Name" AS actor_name,
                g."Name" AS genre_name,
                COUNT(CASE WHEN m.vote_average > 9 THEN ma.movie_id END) AS above_9_count,
                COUNT(CASE WHEN m.vote_average > 8 THEN ma.movie_id END) AS above_8_count,
                COUNT(CASE WHEN m.vote_average > 7 THEN ma.movie_id END) AS above_7_count,
                COUNT(CASE WHEN m.vote_average > 6 THEN ma.movie_id END) AS above_6_count,
                COUNT(CASE WHEN m.vote_average > 5 THEN ma.movie_id END) AS above_5_count,
                COUNT(CASE WHEN m.vote_average < 5 THEN ma.movie_id END) AS below_5_count
            FROM actors AS a
            JOIN movie_actors AS ma ON a."ID" = ma.actor_id
            JOIN movies AS m ON ma.movie_id = m.id
            JOIN movie_genres AS mg ON m.id = mg.movie_id
            JOIN genres AS g ON mg.genre_id = g."ID" """
        
        query_part2 = """ GROUP BY a."Name", g."Name"
            ORDER BY above_9_count DESC, above_8_count DESC, above_7_count DESC, 
                    above_6_count DESC, above_5_count DESC, below_5_count DESC
            LIMIT {limit};"""

        if option == 10:
            actor_high_rated_movie_query = f"""{query_part1} {query_part2}"""
            actor_high_rated_movie_query_sql_df = get_query_results(
                db, actor_high_rated_movie_query, limit
            )
            actor_high_rated_movie_query_sql_df.columns = actor_high_rated_movie_df_cols
            actor_high_rated_movie_chart = create_high_rated_actors_chart(
                actor_high_rated_movie_query_sql_df,"",0
            )
            return html.Div([actor_high_rated_movie_chart])
        
        if option == 11:
            actor_high_rated_movie_genre_query = f"""
                {query_part1}
                WHERE g."Name" = '{name_genre_movie_vote}'
                {query_part2}
                """
            actor_high_rated_movie_genre_query_sql_df = get_query_results(
                db, actor_high_rated_movie_genre_query, limit
            )
            actor_high_rated_movie_genre_query_sql_df.columns = (
                actor_high_rated_movie_df_cols
            )
            actor_high_rated_movie_genre_chart = create_high_rated_actors_chart(
                actor_high_rated_movie_genre_query_sql_df,name_genre_movie_vote,1
            )
            return html.Div(
                [actor_high_rated_movie_genre_chart]
            )
        if option == 12:
            query_sequel_prequel_genre_revenue = """
                        WITH profitability AS (
                    SELECT
                        m.id AS movie_id,
                        (m.revenue / NULLIF(m.budget, 0)) AS profit_margin
                    FROM movies m
                    WHERE m.revenue > 0 AND m.budget > 0
                ),
                movie_genre_profitability AS (
                    SELECT
                        ms.movie_id_1 AS movie_id,
                        g."Name" AS genre_name,
                        p.profit_margin
                    FROM movie_similarity ms
                    JOIN profitability p ON ms.movie_id_1 = p.movie_id
                    JOIN movie_genres mg ON p.movie_id = mg.movie_id
                    JOIN genres g ON mg.genre_id = g."ID" 
                    UNION
                    SELECT
                        ms.movie_id_2 AS movie_id,
                        g."Name" AS genre_name,
                        p.profit_margin
                    FROM movie_similarity ms
                    JOIN profitability p ON ms.movie_id_2 = p.movie_id
                    JOIN movie_genres mg ON p.movie_id = mg.movie_id
                    JOIN genres g ON mg.genre_id = g."ID"
                )
                SELECT
                    genre_name,
                    COUNT(DISTINCT movie_id) AS movie_count,
                    AVG(profit_margin) AS average_profit_margin
                FROM movie_genre_profitability
                GROUP BY genre_name
                ORDER BY average_profit_margin DESC;
                """

            sequel_prequel_genre_revenue_sql_df = get_query_results(
                db, query_sequel_prequel_genre_revenue, limit_prod_comp_value
            )
            sequel_prequel_genre_revenue_sql_df.columns = [
                "genre_name",
                "movie_count",
                "average_profit_margin",
            ]
            sequel_prequel_genre_revenue_chart = create_genre_profitability_chart(
                sequel_prequel_genre_revenue_sql_df
            )
            return html.Div(
                [sequel_prequel_genre_revenue_chart]
            )

    dash_app.layout = html.Div(
        [
            create_navbar(),
            dcc.Tabs(
                id="page-tabs",
                value="contributors",
                children=[
                    dcc.Tab(label="Top Contributors", value="contributor_bar_chart"),
                    dcc.Tab(label="Top Movies by Profit Margin", value="profit_margin_chart"),
                    dcc.Tab(label="High-Revenue Movies", value="top_directors_chart"),
                    dcc.Tab(label="Top Actors by average voting", value="sci_fi_actors_chart"),
                    dcc.Tab(label="Director-Actor Collaborations", value="collaboration_chart"),
                    dcc.Tab(label="Popularity-Revenue Correlation", value="correlation_chart"),
                    dcc.Tab(label="Genre Comparison for Ratings", value="genre_rating_bar_chart"),
                    dcc.Tab(label="Top Production Houses by Revenue", value="production_houses"),
                    dcc.Tab(label="Top Production Houses by Revenue on genre", value="production_houses_genre"),
                    dcc.Tab(label="Top Actors by high-rated movies", value="actors_by_rating"),
                    dcc.Tab(label="Top Actors by high-rated genre wise movies", value="actors_by_genre"),
                    dcc.Tab(label="Sequel/Prequel Revenue", value="sequel_prequel"),
                ],                
                style={
                    "backgroundColor": "#87a5d6",
                    "border": "1px 1px 1px 1px solid #ddd",
                    "borderRadius": "5px"
                },
            ),            
            html.Div(id="page-content", style={
                "backgroundColor": "#fff0f0",
                "border-top": "10px solid #ddd",
                "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.1)"
            }),
        ]
    )

    @dash_app.callback(
        Output("page-content", "children"),
        Input("page-tabs", "value")
    )
    def render_page(tab):
        if tab == "contributor_bar_chart":
            return html.Div([
                html.Label("Select Entity Type:"),
                dcc.Dropdown(
                    id='entity-type-dropdown-1',
                    options=[
                        {"label": "Directors", "value": "directors"},
                        {"label": "Actors", "value": "actors"},
                        {"label": "Production Companies", "value": "production_companies"},
                    ],
                    value='directors', 
                ),
                
                html.Label("Limit for Contributors:"),
                dcc.Input(
                    id='limit-contributors-input',
                    type='number',
                    value=5,  
                    min=1,  
                    step=1,  
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=1,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="contributor-chart-container", style={"marginTop": "30px"}),
            ])
        elif tab == "profit_margin_chart":
            return html.Div([
                html.Label("Limit for Movies by Profit Margin:"),
                dcc.Input(
                    id='limit-movies-input',
                    type='number',
                    value=5,  
                    min=1,  
                    step=1, 
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=2,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="top-movies-chart-container", style={"marginTop": "30px"}),
            ])
        elif tab == "top_directors_chart":
            return html.Div([
                html.Label("Select Entity Type:"),
                dcc.Dropdown(
                    id='entity-type-dropdown-2',  # Use unique ID
                    options=[
                        {"label": "Directors", "value": "directors"},
                        {"label": "Actors", "value": "actors"},
                        {"label": "Production Companies", "value": "production_companies"},
                    ],
                    value='directors',
                ),
                html.Label("Limit for Top Grossing High-Revenue Movies:"),
                dcc.Input(
                    id='limit-movies-input',
                    type='number',
                    value=100,
                    min=1,
                    step=1,
                ),
                html.Label("Limit for Top Directors by High-Revenue Movies : "),
                dcc.Input(
                    id="limit-directors-input",
                    type="number",
                    value=5,
                    min=1,
                    step=1,
                    placeholder="Enter limit for Directors",
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=3,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="top-directors-chart-container", style={"marginTop": "30px"}),
            ])
        elif tab == "sci_fi_actors_chart":
            return html.Div([
                html.Label("Select Genre:"),
                dcc.Dropdown(
                    id='name-genre-actors-vote-dropdown',
                    options=Genre_List,
                    value="Science Fiction",
                ),
                html.Label("Limit for Sci-Fi Actors:"),
                dcc.Input(
                    id='limit-sci-fi-actors-input',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=4,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="sci-fi-actors-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "collaboration_chart":
            return html.Div([
                html.Label("Limit for Collaborations:"),
                dcc.Input(
                    id='limit-collaborations-input',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=5,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="collaboration-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "correlation_chart":
            return html.Div([
                dcc.Input(
                    id='option',
                    type='number',
                    value=6,  # Default value
                    style={'display': 'none'}  # Hide option input
                ), 
                html.Div(id="popularity-revenue-correlation-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "genre_rating_bar_chart":
            return html.Div([
                html.Label("Select Genre 1:"),
                dcc.Dropdown(
                    id='name-compare-genre1-dropdown',
                    options=Genre_List,
                    value="Action",
                ),
                html.Label("Select Genre 2:"),
                dcc.Dropdown(
                    id='name-compare-genre2-dropdown',
                    options=Genre_List,
                    value="Comedy",
                ),
                html.Label("Limit for Actors Ratings:"),
                dcc.Input(
                    id='limit-actors-ratings-input',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=7,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="genre-rating-bar-chart-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "production_houses":
            return html.Div([
                html.Label("Limit for Production Companies:"),
                dcc.Input(
                    id='limit-prod-comp-value',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=8,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="production-houses-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "production_houses_genre":
            return html.Div([
                html.Label("Select Genre:"),
                dcc.Dropdown(
                    id='name-prod-comp-genre-dropdown',
                    options=Genre_List,
                    value="Action",
                ),
                html.Label("Limit for Production Companies:"),
                dcc.Input(
                    id='limit-prod-comp-genre-value',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=9,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="production_houses_genre-dashboard", style={"marginTop": "30px"}),
            ])
        elif tab == "actors_by_rating":
            return html.Div([
                html.Label("Limit for Actors:"),
                dcc.Input(
                    id='limit-actors-ratings-input',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=10,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="actors_by_rating", style={"marginTop": "30px"}),
            ])
        elif tab == "actors_by_genre":
            return html.Div([
                html.Label("Select Genre:"),
                dcc.Dropdown(
                    id='name-compare-genre1-dropdown',
                    options=Genre_List,
                    value="Action",
                ),
                html.Label("Limit for Actors:"),
                dcc.Input(
                    id='limit-actors-ratings-input',
                    type='number',
                    value=5,
                    min=1,
                    step=1,
                ),
                dcc.Input(
                    id='option',
                    type='number',
                    value=11,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="actors_by_genre", style={"marginTop": "30px"}),
            ])
        elif tab == "sequel_prequel":
            return html.Div([
                dcc.Input(
                    id='option',
                    type='number',
                    value=12,  # Default value
                    style={'display': 'none'}  # Hide option input
                ),
                html.Div(id="sequel-prequel-dashboard", style={"marginTop": "30px"}),
            ])

    @dash_app.callback(
        Output('contributor-chart-container', 'children'),
        [Input('entity-type-dropdown-1', 'value'),
        Input('limit-contributors-input', 'value'),
        Input('option', 'value')]
    )
    def update_contributor_chart(entity_type, limit_contributors, option):
        print("Option: ", option)
        data = render_dashboard(
            option=option,
            entity_type=entity_type,
            limit=limit_contributors,
        )
        return html.Div([data])

    @dash_app.callback(
        Output('top-directors-chart-container', 'children'),
        [Input('entity-type-dropdown-2', 'value'),
        Input('limit-movies-input', 'value'),
        Input('limit-directors-input', 'value'),
        Input('option', 'value')]
    )
    def update_top_directors_chart(entity_type_movie_revenue,limit_directors,limit_movies,option):
        print("Entity Type Movie Revenue: ", limit_movies)
        data = render_dashboard(
            option=option,
            entity_type=entity_type_movie_revenue,
            limit=limit_movies,
            limit_movies=limit_directors,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('top-movies-chart-container', 'children'),
        [Input('limit-movies-input', 'value'),
        Input('option', 'value')]
    )
    def update_profit_margin_chart(limit_movies, option):
        data = render_dashboard(
            option=option,
            limit_movies=limit_movies,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('sci-fi-actors-dashboard', 'children'),
        [Input('name-genre-actors-vote-dropdown', 'value'),
        Input('limit-sci-fi-actors-input', 'value'),
        Input('option', 'value')]
    )
    def update_sci_fi_actors_chart(name_genre_actors_vote, limit_sci_fi_actors, option):
        print("Name Genre Actors Vote: ", name_genre_actors_vote)
        data = render_dashboard(
            option=option,
            name_genre_actors_vote=name_genre_actors_vote,
            limit_sci_fi_actors=limit_sci_fi_actors,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('collaboration-dashboard', 'children'),
        [Input('limit-collaborations-input', 'value'),
        Input('option', 'value')]
    )
    def update_collaboration_chart(limit_collaborations, option):
        data = render_dashboard(
            option=option,
            limit_collaborations=limit_collaborations,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('popularity-revenue-correlation-dashboard', 'children'),
        [Input('option', 'value')]
    )
    def update_correlation_chart(option):
        data = render_dashboard(
            option=option,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('genre-rating-bar-chart-dashboard', 'children'),
        [Input('name-compare-genre1-dropdown', 'value'),
        Input('name-compare-genre2-dropdown', 'value'),
        Input('limit-actors-ratings-input', 'value'),
        Input('option', 'value')]
    )
    def update_genre_rating_bar_chart(name_compare_genre1, name_compare_genre2, limit_actors_ratings, option):
        data = render_dashboard(
            option=option,
            name_compare_genre1=name_compare_genre1,
            name_compare_genre2=name_compare_genre2,
            limit_actors_ratings=limit_actors_ratings,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('production-houses-dashboard', 'children'),
        [Input('limit-prod-comp-value', 'value'),
        Input('option', 'value')]
    )
    def update_production_houses_chart(limit_prod_comp_value, option):
        data = render_dashboard(
            option=option,
            limit_prod_comp_value=limit_prod_comp_value,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('production_houses_genre-dashboard', 'children'),
        [Input('name-prod-comp-genre-dropdown', 'value'),
        Input('limit-prod-comp-genre-value', 'value'),
        Input('option', 'value')]
    )
    def update_actors_by_genre_chart(name_prod_comp_genre, limit_prod_comp_genre_value, option):
        data = render_dashboard(
            option=option,
            name_prod_comp_genre=name_prod_comp_genre,
            limit_prod_comp_genre_value=limit_prod_comp_genre_value,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('actors_by_rating', 'children'),
        [Input('limit-actors-ratings-input', 'value'),
         Input('option', 'value')]
    )
    def update_high_rated_actors_chart(limit,option):
        data = render_dashboard(
            limit=limit,
            option=option,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('actors_by_genre', 'children'),
        [Input('name-compare-genre1-dropdown', 'value'),
         Input('limit-actors-ratings-input', 'value'),
         Input('option', 'value')]
    )
    def update_high_rated_actors_genre_chart(name_compare_genre1, limit, option):
        data = render_dashboard(
            name_genre_movie_vote = name_compare_genre1,
            limit=limit,
            option=option,
        )
        return html.Div([data])
    
    @dash_app.callback(
        Output('sequel-prequel-dashboard', 'children'),
        [Input('option', 'value')]
    )
    def update_sequel_prequel_chart(option):
        data = render_dashboard(
            option=option,
        )
        return html.Div([data])
    
    