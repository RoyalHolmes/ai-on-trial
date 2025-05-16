import streamlit as st
import pandas as pd
import json
import pydeck as pdk
import altair as alt
import plotly.express as px

# Load the data
with open("ai_on_trial_data_static_geo.json") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Consolidate regional labels
df["region"] = df["region"].replace({
    "Europe": "European Union"
})

# Sidebar navigation
st.sidebar.image("logo.png", width=100)
st.sidebar.title("AI on Trial Navigation")
view = st.sidebar.radio("Go to:", ["Home", "Search Cases", "Global Map", "Trends Over Time", "Issue Composition by Country"])

# Ensure filtered_df is always available
filtered_df = df.copy()

# Sidebar filters (only for "Search Cases")
if view == "Search Cases":
    st.sidebar.title("Filter Cases")
    search_term = st.sidebar.text_input("Search by case or summary")

    countries = ["All"] + sorted(df["region"].dropna().unique())
    selected_country = st.sidebar.selectbox("Country/Region", countries)

    issues = ["All"] + sorted(df["issue"].dropna().unique())
    selected_issue = st.sidebar.selectbox("AI-related Issue", issues)

    years = ["All"] + sorted(df["year"].dropna().astype(int).unique())
    selected_year = st.sidebar.selectbox("Year", years)

    # Apply filters
    if search_term:
        filtered_df = filtered_df[
            filtered_df["caseName"].str.contains(search_term, case=False, na=False)
            | filtered_df["summary"].str.contains(search_term, case=False, na=False)
        ]

    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["region"] == selected_country]

    if selected_issue != "All":
        filtered_df = filtered_df[filtered_df["issue"] == selected_issue]

    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["year"] == int(selected_year)]

# --- Main Views ---

if view == "Home":
    total_cases = len(df)
    unique_issues = df['issue'].nunique()
    countries = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("📁 Total Cases", total_cases)
    col2.metric("🧠 AI-Related Issues", unique_issues)
    col3.metric("🌍 Countries/Regions", countries)
    top_issues = df['issue'].value_counts().head(3)
    st.markdown("### 🔍 Top 3 Issues")
    for issue, count in top_issues.items():
        st.write(f"- **{issue}**: {count} cases")
    
    st.markdown("""
    # 🤖 AI on Trial

    Artificial intelligence is already reshaping our world, through innovation, but also through conflict and harms.  

    Yet, much of the global conversation around **AI governance** treats regulation as a future challenge, overlooking the fact that **AI is already being contested in courts** around the world.

    This project began as a response to that gap. While AI incident databases have gained visibility, we realized there was no comprehensive resource tracking the **legal disputes** these technologies are generating, across countries, contexts, and areas of law.

    **AI on Trial** aims to become that resource:  
    A dynamic, open, and evolving portal to understand how AI is being governed through judicial decisions, not just through principles or abstract policy.

    We’ve documented **litigated AI-related cases** in **39 regions** to date (Argentina, Australia, Belgium, Brazil, Canada, Chile, China, Colombia, Czech Republic, Denmark, European Union, Finland, France, Germany, Greece, Hungary, India, Indonesia, Ireland, Israel, Italy, Japan, Kenya, Mexico, Namibia, Netherlands, Pery, Portugal, Russia, Singapore, South Africa, South Korea, Spain, Sweden, Uganda, United Kingdom, United States, Uruguay and Zimbabwe).

    This dashboard does **not claim to be exhaustive**. It’s a work in progress, and for now, a **one-person project**. Your suggestions, corrections, and additions are warmly welcomed.

    📬 Reach out: [isadoravaladares@usp.br](mailto:isadoravaladares@usp.br)
    """)

elif view == "Search Cases":
    st.title("Searchable Case List")
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['caseName']} ({row['year']})"):
            st.write(f"**Region:** {row['region']}")
            st.write(f"**Court:** {row['court']}")
            st.write(f"**Issue:** {row['issue']}")
            st.write(f"**Final Decision:** {row['finalDecision']}")
            st.write(f"**Summary:** {row['summary']}")
            st.write(f"**Excerpt:** {row['excerpt']}")
            st.markdown(f"[🔗 View Full Decision]({row['link']})")

elif view == "Global Map":
    st.title("Global Case Map")

    # Load GeoJSON file for choropleth
    with open("choropleth_ai_cases.geojson") as f:
        geojson_data = json.load(f)

    # Create Pydeck Layer
    choropleth_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geojson_data,
        opacity=0.8,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255],
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1.2)

    st.pydeck_chart(pdk.Deck(
        layers=[choropleth_layer],
        initial_view_state=view_state,
        map_style="light",
        tooltip={"text": "Country: {name}\nCases: {cases}"}
    ))

    st.markdown("""
    **Legend (Cases by Country):**

    <span style='display: inline-block; width: 12px; height: 12px; background-color: rgb(230,230,230); border-radius: 2px;'></span>  0 cases  
    <span style='display: inline-block; width: 12px; height: 12px; background-color: rgb(180,200,240); border-radius: 2px;'></span>  1–5 cases  
    <span style='display: inline-block; width: 12px; height: 12px; background-color: rgb(120,150,210); border-radius: 2px;'></span>  6–15 cases  
    <span style='display: inline-block; width: 12px; height: 12px; background-color: rgb(70,100,180); border-radius: 2px;'></span>  16–30 cases  
    <span style='display: inline-block; width: 12px; height: 12px; background-color: rgb(30,60,140); border-radius: 2px;'></span>  31+ cases
    """, unsafe_allow_html=True)

elif view == "Trends Over Time":
    st.title("Trends Over Time")

    # User selection for grouping and chart type
    group_by = st.selectbox("Group by:", ["None", "Region", "Issue"])
    chart_type = st.radio("Chart Type:", ["Line", "Area", "Bar"])

    # Fix capitalization for Altair (match real column names)
    group_column = None
    if group_by == "Region":
        group_column = "region"
    elif group_by == "Issue":
        group_column = "issue"

    # Apply grouping logic
    trend_data = filtered_df.copy()
    if group_column:
        trend_data = trend_data.groupby(["year", group_column]).size().reset_index(name="Number of Cases")
    else:
        trend_data = trend_data.groupby("year").size().reset_index(name="Number of Cases")

    # Build the chart
    chart = alt.Chart(trend_data).encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("Number of Cases", title="Cases"),
        tooltip=["year", "Number of Cases"]
    )

    if group_column:
        chart = chart.encode(
            color=alt.Color(group_column, 
                        scale=alt.Scale(scheme='category20'),  # or 'tableau20', 'set3', etc.
                        legend=alt.Legend(title=group_by)
                       )
    )


    if chart_type == "Line":
        chart = chart.mark_line(point=True)
    elif chart_type == "Area":
        chart = chart.mark_area(opacity=0.6)
    else:
        chart = chart.mark_bar()

    st.altair_chart(chart, use_container_width=True)

elif view == "Issue Composition by Country":
    st.title("Issue Composition by Country")

    countries = sorted(df["region"].dropna().unique())
    selected_countries = st.multiselect("Select up to 3 countries:", countries, default=countries[:1])

    if len(selected_countries) == 1:
        col1, _ = st.columns(2)
        country_data = df[df["region"] == selected_countries[0]]
        issue_counts = country_data["issue"].value_counts().reset_index()
        issue_counts.columns = ["Issue", "Count"]
        fig = px.treemap(issue_counts, path=["Issue"], values="Count", color="Count", color_continuous_scale="Blues")
        col1.subheader(selected_countries[0])
        col1.plotly_chart(fig, use_container_width=True)

    elif len(selected_countries) == 2:
        col1, col2 = st.columns(2)
        for idx, col in enumerate([col1, col2]):
            country_data = df[df["region"] == selected_countries[idx]]
            issue_counts = country_data["issue"].value_counts().reset_index()
            issue_counts.columns = ["Issue", "Count"]
            fig = px.treemap(issue_counts, path=["Issue"], values="Count", color="Count", color_continuous_scale="Blues")
            col.subheader(selected_countries[idx])
            col.plotly_chart(fig, use_container_width=True)
            
    elif len(selected_countries) == 3:
        col1, col2, col3 = st.columns(3)
        for idx, col in enumerate([col1, col2, col3]):
            country_data = df[df["region"] == selected_countries[idx]]
            issue_counts = country_data["issue"].value_counts().reset_index()
            issue_counts.columns = ["Issue", "Count"]
            fig = px.treemap(issue_counts, path=["Issue"], values="Count", color="Count", color_continuous_scale="Blues")
            col.subheader(selected_countries[idx])
            col.plotly_chart(fig, use_container_width=True)

    elif len(selected_countries) > 3:
        st.warning("Please select only up to 3 countries for comparison.")
