import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- Settings ----------
FILE = "expenses.csv"
COLUMNS = ["date", "category", "description", "amount"]
CURRENCY = "₹"  # change to "$", "€", etc.
DEFAULT_BUDGETS = {"Food": 8000, "Transport": 3000, "Entertainment": 2000}
ICONS = {
    "Food": "🍽️", "Transport": "🚌", "Entertainment": "🎬",
    "Bills": "💡", "Shopping": "🛍️", "Health": "💊",
}

# Palette: ink navy base, marigold accent, teal = on track, coral = over budget
MARIGOLD, TEAL, CORAL = "#F2A93B", "#3FB8A5", "#E4572E"
PALETTE = [MARIGOLD, TEAL, "#5B8DEF", "#B084E0", CORAL, "#8BC17A", "#D9C7A0"]

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600&display=swap');

html, body, [class*="css"], .stMarkdown, .stDataFrame, label, input, button {
    font-family: 'DM Sans', sans-serif;
}
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }

/* Hero: the total is the one loud thing on the page */
.hero { padding: 0.5rem 0 1.6rem 0; border-bottom: 1px solid #26395A; margin-bottom: 1.4rem; }
.hero-sub { color: #8FA0BA; font-size: 1rem; margin-bottom: 0.2rem; }
.hero-total {
    font-family: 'Fraunces', serif; font-weight: 600;
    font-size: 4.2rem; line-height: 1.05; color: #F2A93B;
}
.hero-note { color: #8FA0BA; margin-top: 0.4rem; }

/* Quiet, flat metric tiles */
div[data-testid="stMetric"] {
    background: #16263D; border: 1px solid #26395A;
    border-radius: 10px; padding: 0.9rem 1.1rem;
}
div[data-testid="stMetricLabel"] { color: #8FA0BA; }
div[data-testid="stMetricValue"] { font-weight: 700; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #26395A; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 8px 18px; }
.stTabs [aria-selected="true"] { color: #F2A93B !important; }

/* Budget rows */
.budget { background: #16263D; border: 1px solid #26395A; border-radius: 10px;
          padding: 0.9rem 1.1rem; margin-bottom: 0.7rem; }
.budget-top { display: flex; justify-content: space-between; font-weight: 500; }
.budget-top span:last-child { color: #8FA0BA; font-weight: 400; }
.track { background: #0F1B2D; border-radius: 99px; height: 8px; margin: 0.6rem 0 0.4rem 0; overflow: hidden; }
.fill { height: 8px; border-radius: 99px; }
.budget-note { font-size: 0.9rem; }

section[data-testid="stSidebar"] { border-right: 1px solid #26395A; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Helpers ----------
def money(x):
    return f"{CURRENCY}{x:,.0f}"


def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=COLUMNS)
        df["date"] = pd.to_datetime(df["date"])
    return df


def save_data(df):
    df.to_csv(FILE, index=False)


def add_expense(d, category, description, amount):
    df = load_data()
    new_row = pd.DataFrame([{
        "date": pd.to_datetime(d),
        "category": category.strip().title(),
        "description": description,
        "amount": float(amount),
    }])
    save_data(pd.concat([df, new_row], ignore_index=True))


def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="DM Sans, sans-serif", color="#EEF1F6"),
        title_font=dict(size=16),
        legend=dict(orientation="h", y=-0.12),
    )
    fig.update_xaxes(gridcolor="#26395A", zeroline=False)
    fig.update_yaxes(gridcolor="#26395A", zeroline=False)
    return fig


def budget_row(cat, used, limit):
    limit = max(limit, 1)
    pct = used / limit * 100
    color = TEAL if pct < 75 else MARIGOLD if pct < 100 else CORAL
    if used > limit:
        note = f"Over budget by {money(used - limit)}"
    else:
        note = f"{money(limit - used)} left"
    html = (
        '<div class="budget">'
        f'<div class="budget-top"><span>{ICONS.get(cat, "📦")} {cat}</span>'
        f"<span>{money(used)} of {money(limit)}</span></div>"
        f'<div class="track"><div class="fill" style="width:{min(pct, 100):.0f}%;background:{color};"></div></div>'
        f'<div class="budget-note" style="color:{color}">{pct:.0f}% used, {note}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------- Sidebar ----------
df = load_data()
known_cats = sorted(set(df["category"].dropna()) | set(DEFAULT_BUDGETS))

st.sidebar.header("Add an expense")
with st.sidebar.form("add_form", clear_on_submit=True):
    d = st.date_input("Date", value=date.today())
    picked = st.selectbox("Category", known_cats)
    new_cat = st.text_input("Or type a new category")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=50.0)
    submitted = st.form_submit_button("Save expense")

if submitted:
    if amount > 0:
        add_expense(d, new_cat.strip() or picked, description, amount)
        st.sidebar.success("Expense saved.")
        st.rerun()
    else:
        st.sidebar.error("Enter an amount above 0.")

with st.sidebar.expander("Monthly budgets"):
    budgets = {
        c: st.number_input(c, min_value=0, value=v, step=500)
        for c, v in DEFAULT_BUDGETS.items()
    }

# ---------- Empty state ----------
if df.empty:
    st.title("Expense Tracker")
    st.info("No expenses yet. Use the form on the left to add your first one.")
    st.stop()

df["month"] = df["date"].dt.strftime("%Y-%m")

# ---------- Filters ----------
f1, f2 = st.columns(2)
months = ["All"] + sorted(df["month"].unique(), reverse=True)
sel_month = f1.selectbox(
    "Month",
    months,
    format_func=lambda m: m if m == "All" else pd.to_datetime(m).strftime("%B %Y"),
)
sel_cats = f2.multiselect("Categories", sorted(df["category"].unique()), placeholder="All categories")

view = df.copy()
if sel_month != "All":
    view = view[view["month"] == sel_month]
if sel_cats:
    view = view[view["category"].isin(sel_cats)]

# ---------- Hero ----------
scope = "all time" if sel_month == "All" else pd.to_datetime(sel_month).strftime("%B %Y")
n_cats = view["category"].nunique()
st.markdown(
    f'<div class="hero"><div class="hero-sub">Total spent, {scope}</div>'
    f'<div class="hero-total">{money(view["amount"].sum())}</div>'
    f'<div class="hero-note">{len(view)} expenses across {n_cats} categories</div></div>',
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
m1.metric("Average expense", money(view["amount"].mean()) if not view.empty else "-")
m2.metric("Largest expense", money(view["amount"].max()) if not view.empty else "-")
top_cat = view.groupby("category")["amount"].sum().idxmax() if not view.empty else "-"
m3.metric("Top category", f"{ICONS.get(top_cat, '')} {top_cat}".strip())

st.write("")
tab_list, tab_charts, tab_budget, tab_edit = st.tabs(
    ["Expenses", "Charts", "Budget", "Edit or delete"]
)

# ---------- Expenses ----------
with tab_list:
    disp = view.sort_values("date", ascending=False).copy()
    disp["category"] = disp["category"].map(lambda c: f"{ICONS.get(c, '📦')} {c}")
    st.dataframe(
        disp[COLUMNS],
        hide_index=True,
        width="stretch",
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "category": "Category",
            "description": "Description",
            "amount": st.column_config.NumberColumn("Amount", format=f"{CURRENCY}%.0f"),
        },
    )
    st.download_button(
        "Download as CSV",
        view[COLUMNS].to_csv(index=False),
        file_name="expenses_export.csv",
        mime="text/csv",
    )

# ---------- Charts ----------
with tab_charts:
    if view.empty:
        st.warning("No expenses match these filters.")
    else:
        c1, c2 = st.columns(2)

        by_cat = view.groupby("category", as_index=False)["amount"].sum()
        fig = px.pie(by_cat, names="category", values="amount", hole=0.58,
                     color_discrete_sequence=PALETTE, title="Where the money went")
        fig.update_traces(textinfo="percent", marker=dict(line=dict(color="#0F1B2D", width=2)))
        c1.plotly_chart(style_chart(fig), width="stretch")

        monthly = df.groupby("month", as_index=False)["amount"].sum()
        fig = px.bar(monthly, x="month", y="amount", title="Spending by month",
                     color_discrete_sequence=[MARIGOLD])
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        c2.plotly_chart(style_chart(fig), width="stretch")

        top5 = view.nlargest(5, "amount")
        fig = px.bar(top5, x="amount", y="description", orientation="h",
                     title="Five biggest expenses", color_discrete_sequence=[TEAL])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(style_chart(fig, 320), width="stretch")

# ---------- Budget ----------
with tab_budget:
    b_month = sel_month if sel_month != "All" else date.today().strftime("%Y-%m")
    st.subheader(f"Budget for {pd.to_datetime(b_month).strftime('%B %Y')}")
    spent = df[df["month"] == b_month].groupby("category")["amount"].sum()
    for cat, limit in budgets.items():
        budget_row(cat, float(spent.get(cat, 0)), limit)
    st.caption("Change the limits from Monthly budgets in the sidebar.")

# ---------- Edit or delete ----------
with tab_edit:
    st.caption(
        "Click any cell to change it. To delete, tick the box at the left of a row "
        "and press Delete on your keyboard (or click the trash icon). "
        "Click Save changes when you're done."
    )

    editable = df[COLUMNS].copy()
    editable["date"] = pd.to_datetime(editable["date"]).dt.date
    editable = editable.sort_values("date", ascending=False).reset_index(drop=True)

    edited = st.data_editor(
        editable,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        key="expense_editor",
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY", required=True),
            "category": st.column_config.TextColumn("Category", required=True),
            "description": st.column_config.TextColumn("Description"),
            "amount": st.column_config.NumberColumn(
                "Amount", min_value=0, format=f"{CURRENCY}%.0f", required=True
            ),
        },
    )

    if st.button("Save changes", type="primary"):
        clean = edited.dropna(subset=["date", "category", "amount"]).copy()
        clean["category"] = clean["category"].str.strip().str.title()
        clean["date"] = pd.to_datetime(clean["date"])
        save_data(clean[COLUMNS])
        st.toast("Changes saved")
        st.rerun()