import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Nassau Candy – Profitability Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5c;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #a78bfa; }
    .metric-label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Nassau_Candy_Distributor.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True, errors="coerce")
    for col in ["Sales", "Units", "Gross Profit", "Cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["Sales"] > 0]
    df = df[df["Gross Profit"].notna()]
    df = df[df["Units"] > 0]
    df["Gross Margin (%)"] = (df["Gross Profit"] / df["Sales"]) * 100
    df["Profit per Unit"]  = df["Gross Profit"] / df["Units"]
    df["Cost per Unit"]    = df["Cost"] / df["Units"]
    df["Product Name"]     = df["Product Name"].str.strip()
    return df

df_raw = load_data()

with st.sidebar:
    st.title("🍬 Filters")
    min_date = df_raw["Order Date"].min().date()
    max_date = df_raw["Order Date"].max().date()
    date_range = st.date_input("Order Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    divisions = sorted(df_raw["Division"].dropna().unique().tolist())
    selected_div = st.multiselect("Division", options=divisions, default=divisions)
    regions = sorted(df_raw["Region"].dropna().unique().tolist())
    selected_reg = st.multiselect("Region", options=regions, default=regions)
    margin_thresh = st.slider("Minimum Gross Margin (%)", 0, 100, 0, step=5)
    product_search = st.text_input("🔍 Product Search", placeholder="e.g. Wonka")
    st.markdown("---")
    st.caption("Nassau Candy Distributor | Dashboard v1.0")

df = df_raw.copy()
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["Order Date"] >= start_d) & (df["Order Date"] <= end_d)]
if selected_div:
    df = df[df["Division"].isin(selected_div)]
if selected_reg:
    df = df[df["Region"].isin(selected_reg)]
df = df[df["Gross Margin (%)"] >= margin_thresh]
if product_search.strip():
    df = df[df["Product Name"].str.contains(product_search.strip(), case=False, na=False)]

st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Profitability Analytics Dashboard")
st.markdown(f"Showing **{len(df):,}** records after filters")

if df.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar.")
    st.stop()

total_sales  = df["Sales"].sum()
total_profit = df["Gross Profit"].sum()
avg_margin   = (total_profit / total_sales * 100) if total_sales else 0
total_units  = df["Units"].sum()
profit_pu    = total_profit / total_units if total_units else 0

k1, k2, k3, k4, k5 = st.columns(5)
def kpi(col, label, value):
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{value}</div>
        <div class='metric-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Total Revenue",      f"${total_sales:,.0f}")
kpi(k2, "Total Gross Profit", f"${total_profit:,.0f}")
kpi(k3, "Avg Gross Margin",   f"{avg_margin:.1f}%")
kpi(k4, "Total Units Sold",   f"{total_units:,}")
kpi(k5, "Avg Profit / Unit",  f"${profit_pu:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Product Profitability",
    "🏭 Division Performance",
    "💰 Cost & Margin Diagnostics",
    "📊 Profit Concentration (Pareto)",
])

# ── TAB 1 ──────────────────────────────────────────────────────────────────
with tab1:
    st.header("Product-Level Profitability")
    prod = (
        df.groupby("Product Name")
        .agg(Total_Sales=("Sales","sum"), Total_Profit=("Gross Profit","sum"),
             Total_Units=("Units","sum"), Total_Cost=("Cost","sum"),
             Orders=("Order ID","nunique"))
        .reset_index()
    )
    prod["Gross Margin (%)"]  = (prod["Total_Profit"] / prod["Total_Sales"] * 100).round(2)
    prod["Profit per Unit"]   = (prod["Total_Profit"] / prod["Total_Units"]).round(2)
    prod["Revenue Share (%)"] = (prod["Total_Sales"]  / prod["Total_Sales"].sum() * 100).round(2)
    prod["Profit Share (%)"]  = (prod["Total_Profit"] / prod["Total_Profit"].sum() * 100).round(2)
    prod = prod.sort_values("Total_Profit", ascending=False)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(prod.head(15), x="Total_Profit", y="Product Name",
                     orientation="h", color="Gross Margin (%)",
                     color_continuous_scale="Viridis",
                     title="Top Products by Gross Profit",
                     labels={"Total_Profit": "Gross Profit ($)"})
        fig.update_layout(yaxis=dict(autorange="reversed"), height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.bar(prod.sort_values("Gross Margin (%)").tail(15),
                      x="Gross Margin (%)", y="Product Name",
                      orientation="h", color="Gross Margin (%)",
                      color_continuous_scale="RdYlGn",
                      title="Gross Margin % by Product")
        fig2.update_layout(yaxis=dict(autorange="reversed"), height=450)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Sales vs Gross Margin (bubble = total profit)")
    fig3 = px.scatter(prod, x="Total_Sales", y="Gross Margin (%)",
                      size="Total_Profit", color="Product Name",
                      hover_name="Product Name", size_max=60,
                      title="Revenue vs Margin Matrix",
                      labels={"Total_Sales": "Total Revenue ($)"})
    fig3.add_hline(y=avg_margin, line_dash="dash", line_color="red",
                   annotation_text=f"Avg Margin {avg_margin:.1f}%")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📋 Product Margin Leaderboard")
    disp = prod[["Product Name","Total_Sales","Total_Profit","Gross Margin (%)","Profit per Unit","Revenue Share (%)","Profit Share (%)"]].copy()
    disp.columns = ["Product","Revenue ($)","Gross Profit ($)","Margin (%)","Profit/Unit ($)","Rev Share (%)","Profit Share (%)"]
    disp = disp.reset_index(drop=True)
    st.dataframe(
        disp.style.format({
            "Revenue ($)": "${:,.2f}", "Gross Profit ($)": "${:,.2f}",
            "Margin (%)": "{:.1f}%", "Profit/Unit ($)": "${:.2f}",
            "Rev Share (%)": "{:.1f}%", "Profit Share (%)": "{:.1f}%",
        }),
        use_container_width=True, height=420
    )

# ── TAB 2 ──────────────────────────────────────────────────────────────────
with tab2:
    st.header("Division-Level Performance")
    div_agg = (
        df.groupby("Division")
        .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"),
             Cost=("Cost","sum"), Units=("Units","sum"),
             Orders=("Order ID","nunique"), Products=("Product Name","nunique"))
        .reset_index()
    )
    div_agg["Gross Margin (%)"] = (div_agg["Profit"] / div_agg["Revenue"] * 100).round(2)
    div_agg["Profit per Unit"]  = (div_agg["Profit"] / div_agg["Units"]).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue",      x=div_agg["Division"], y=div_agg["Revenue"],      marker_color="#818cf8"))
        fig.add_trace(go.Bar(name="Gross Profit", x=div_agg["Division"], y=div_agg["Profit"],       marker_color="#34d399"))
        fig.add_trace(go.Bar(name="Cost",         x=div_agg["Division"], y=div_agg["Cost"],         marker_color="#f87171"))
        fig.update_layout(barmode="group", title="Revenue vs Profit vs Cost by Division",
                          yaxis_title="USD ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(div_agg, names="Division", values="Profit",
                      title="Profit Contribution by Division",
                      color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.45)
        fig2.update_traces(textinfo="label+percent")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Gross Margin Distribution by Division")
    fig3 = px.box(df, x="Division", y="Gross Margin (%)", color="Division",
                  points="outliers", title="Margin Spread within Each Division",
                  color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Division Summary Table")
    disp2 = div_agg.copy()
    disp2.columns = ["Division","Revenue ($)","Profit ($)","Cost ($)","Units","Orders","Products","Margin (%)","Profit/Unit ($)"]
    st.dataframe(
        disp2.style.format({
            "Revenue ($)": "${:,.2f}", "Profit ($)": "${:,.2f}",
            "Cost ($)": "${:,.2f}", "Profit/Unit ($)": "${:.2f}",
            "Margin (%)": "{:.1f}%",
        }),
        use_container_width=True
    )

    st.subheader("Margin by Region within Each Division")
    reg_div = (
        df.groupby(["Division","Region"])
        .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
        .reset_index()
    )
    reg_div["Margin (%)"] = (reg_div["Profit"] / reg_div["Revenue"] * 100).round(2)
    fig4 = px.bar(reg_div, x="Region", y="Margin (%)", color="Division",
                  barmode="group", title="Region-wise Margin by Division",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig4, use_container_width=True)

# ── TAB 3 ──────────────────────────────────────────────────────────────────
with tab3:
    st.header("Cost vs Margin Diagnostics")
    prod3 = (
        df.groupby(["Product Name","Division"])
        .agg(Total_Sales=("Sales","sum"), Total_Profit=("Gross Profit","sum"),
             Total_Cost=("Cost","sum"), Total_Units=("Units","sum"))
        .reset_index()
    )
    prod3["Gross Margin (%)"] = (prod3["Total_Profit"] / prod3["Total_Sales"] * 100).round(2)
    prod3["Cost Ratio (%)"]   = (prod3["Total_Cost"]   / prod3["Total_Sales"] * 100).round(2)

    st.subheader("Cost vs Sales — Margin Risk Map")
    fig = px.scatter(prod3, x="Total_Cost", y="Total_Sales",
                     color="Gross Margin (%)", size="Total_Units",
                     hover_name="Product Name", color_continuous_scale="RdYlGn",
                     title="Cost vs Revenue (color = margin, size = units)",
                     labels={"Total_Cost":"Total Cost ($)","Total_Sales":"Total Revenue ($)"})
    max_val = max(prod3["Total_Cost"].max(), prod3["Total_Sales"].max())
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                  line=dict(color="red", dash="dash"))
    fig.add_annotation(x=max_val*0.7, y=max_val*0.65, text="Breakeven Line",
                       showarrow=False, font=dict(color="red"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Revenue vs Cost vs Profit — Waterfall View")
    wf_data = prod3.sort_values("Total_Sales", ascending=False)
    fig2 = go.Figure(go.Waterfall(
        name="Profitability", orientation="v",
        measure=["relative"] * len(wf_data),
        x=wf_data["Product Name"], y=wf_data["Total_Profit"],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig2.update_layout(title="Per-Product Gross Profit Waterfall", height=450)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("⚠️ Margin Risk Flags")
    prod3["Risk"] = pd.cut(
        prod3["Gross Margin (%)"],
        bins=[-np.inf, 30, 50, np.inf],
        labels=["🔴 High Risk (<30%)", "🟡 Medium Risk (30–50%)", "🟢 Healthy (>50%)"],
    )
    risk_table = prod3[["Product Name","Division","Total_Sales","Total_Profit","Gross Margin (%)","Risk"]].copy()
    risk_table.columns = ["Product","Division","Revenue ($)","Profit ($)","Margin (%)","Risk Flag"]
    risk_table = risk_table.sort_values("Margin (%)")
    st.dataframe(
        risk_table.style.format({
            "Revenue ($)": "${:,.2f}", "Profit ($)": "${:,.2f}", "Margin (%)": "{:.1f}%"
        }),
        use_container_width=True, height=400,
    )

    st.subheader("Cost Ratio (%) by Product")
    fig3 = px.bar(prod3.sort_values("Cost Ratio (%)", ascending=False),
                  x="Product Name", y="Cost Ratio (%)", color="Division",
                  title="Cost as % of Revenue by Product",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="50% threshold")
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 4 ──────────────────────────────────────────────────────────────────
with tab4:
    st.header("Profit Concentration (Pareto Analysis)")
    pareto = (
        df.groupby("Product Name")
        .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    pareto["Cumulative Revenue (%)"] = pareto["Revenue"].cumsum() / pareto["Revenue"].sum() * 100
    pareto["Cumulative Profit (%)"]  = pareto["Profit"].cumsum()  / pareto["Profit"].sum()  * 100
    pareto["# Products"] = range(1, len(pareto)+1)

    col1, col2 = st.columns(2)
    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=pareto["Product Name"], y=pareto["Revenue"],
                             name="Revenue", marker_color="#818cf8"), secondary_y=False)
        fig.add_trace(go.Scatter(x=pareto["Product Name"], y=pareto["Cumulative Revenue (%)"],
                                 name="Cumulative %", line=dict(color="#f59e0b", width=3)),
                      secondary_y=True)
        fig.add_hline(y=80, line_dash="dash", line_color="red", secondary_y=True,
                      annotation_text="80%")
        fig.update_layout(title="Revenue Pareto Chart", height=420)
        fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=pareto["Product Name"], y=pareto["Profit"],
                              name="Profit", marker_color="#34d399"), secondary_y=False)
        fig2.add_trace(go.Scatter(x=pareto["Product Name"], y=pareto["Cumulative Profit (%)"],
                                  name="Cumulative %", line=dict(color="#f59e0b", width=3)),
                       secondary_y=True)
        fig2.add_hline(y=80, line_dash="dash", line_color="red", secondary_y=True,
                       annotation_text="80%")
        fig2.update_layout(title="Profit Pareto Chart", height=420)
        fig2.update_yaxes(title_text="Gross Profit ($)", secondary_y=False)
        fig2.update_yaxes(title_text="Cumulative %", secondary_y=True)
        st.plotly_chart(fig2, use_container_width=True)

    products_80_rev = (pareto["Cumulative Revenue (%)"] <= 80).sum() + 1
    products_80_pro = (pareto["Cumulative Profit (%)"]  <= 80).sum() + 1
    total_products  = len(pareto)
    st.info(
        f"📌 **{products_80_rev} out of {total_products} products** drive 80% of Revenue "
        f"({products_80_rev/total_products*100:.0f}% of SKUs)  \n"
        f"📌 **{products_80_pro} out of {total_products} products** drive 80% of Profit "
        f"({products_80_pro/total_products*100:.0f}% of SKUs)"
    )

    st.subheader("📍 Revenue Concentration by State")
    state_rev = (
        df.groupby("State/Province")
        .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    state_rev["Margin (%)"] = (state_rev["Profit"] / state_rev["Revenue"] * 100).round(1)
    fig3 = px.bar(state_rev.head(20), x="State/Province", y="Revenue",
                  color="Margin (%)", color_continuous_scale="RdYlGn",
                  title="Top 20 States by Revenue (color = margin)")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🗺️ Profit by State — US Map")
    state_map = (
        df.groupby("State/Province")
        .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
        .reset_index()
    )
    state_map["Margin (%)"] = (state_map["Profit"] / state_map["Revenue"] * 100).round(1)
    us_states = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
        'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
        'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
        'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH',
        'New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC',
        'North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA',
        'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
        'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
        'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC',
    }
    state_map["Code"] = state_map["State/Province"].map(us_states)
    state_map = state_map.dropna(subset=["Code"])
    fig4 = px.choropleth(
        state_map, locations="Code", locationmode="USA-states",
        color="Profit", scope="usa", color_continuous_scale="Viridis",
        hover_data={"State/Province":True,"Revenue":":$,.0f","Profit":":$,.0f","Margin (%)":":.1f"},
        title="Gross Profit Distribution Across US States",
    )
    fig4.update_layout(height=500)
    st.plotly_chart(fig4, use_container_width=True)

    top3_share = (pareto.head(3)["Revenue"].sum() / pareto["Revenue"].sum() * 100)
    st.subheader("🔺 Over-Dependency Risk")
    st.warning(
        f"**Top 3 products account for {top3_share:.1f}% of total revenue.** "
        + ("HIGH concentration risk — diversification recommended." if top3_share > 50
           else "Concentration risk is moderate.")
    )
    fig5 = px.treemap(pareto, path=["Product Name"], values="Revenue",
                      color="Profit", color_continuous_scale="RdYlGn",
                      title="Revenue Treemap — Size = Revenue, Color = Profit")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption("Nassau Candy Distributor · Profitability Dashboard · Built with Streamlit & Plotly")
