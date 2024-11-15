from dash import html
import dash_bootstrap_components as dbc

def create_navbar(user_id="user"):
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Nav(
                    [
                        dbc.NavItem(html.Span(f"Hello, {user_id}", className="me-3")),
                        # dbc.NavItem(dbc.NavLink("Logout", href="/logout", className="nav-link")),
                    ],
                    className="d-flex align-items-center ms-auto",
                    navbar=True,
                ),
            ]
        ),
        className="navbar",
        color="dark",
        dark=True,
    )
