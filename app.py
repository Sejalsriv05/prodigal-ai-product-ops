import streamlit as st
import json
import pandas as pd

from agents import (
    strategy_agent,
    content_agent,
    creative_agent,
    publisher_agent,
    analytics_agent,
    create_week2_brief
)

st.set_page_config(
    page_title="AI Campaign Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0b0f0d;
        color: #e8f5e9;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    h1, h2, h3 {
        color: #8aff9c;
    }

    .card {
        background: #111815;
        border: 1px solid #26352d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .metric-card {
        background: #111815;
        border: 1px solid #26352d;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    .status {
        color: #8aff9c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "state" not in st.session_state:
    st.session_state.state = None

if "week1_report" not in st.session_state:
    st.session_state.week1_report = None

if "week1_published" not in st.session_state:
    st.session_state.week1_published = None

if "week2_state" not in st.session_state:
    st.session_state.week2_state = None

if "week2_report" not in st.session_state:
    st.session_state.week2_report = None

if "week2_published" not in st.session_state:
    st.session_state.week2_published = None


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI-Powered Campaign Agent")
st.caption("Plan → Create → Human Review → Publish → Analyze → Improve")

st.divider()


# ============================================================
# CAMPAIGN INPUT
# ============================================================

st.subheader("1. Campaign Brief")

brief = st.text_area(
    "Enter your campaign prompt",
    value=(
        "We are launching a budget espresso machine "
        "for students. Run a short awareness campaign."
    ),
    height=130
)

if st.button("🚀 Generate Campaign Plan", use_container_width=True):

    if not brief.strip():
        st.error("Please enter a campaign brief.")
    else:

        initial_state = {
            "human_brief": brief,
            "target_audience": "",
            "channel_mix": [],
            "drafted_posts": [],
            "feedback": ""
        }

        with st.spinner("Strategy Agent is planning..."):
            strategy = strategy_agent(initial_state)

        state = {**initial_state, **strategy}

        with st.spinner("Content Writer Agent is creating posts..."):
            content = content_agent(state)

        state = {**state, **content}

        with st.spinner("Creative Agent is refining the content..."):
            creative = creative_agent(state)

        state = {**state, **creative}

        st.session_state.state = state
        st.session_state.week1_report = None
        st.session_state.week1_published = None
        st.session_state.week2_state = None
        st.session_state.week2_report = None
        st.session_state.week2_published = None

        st.success("Campaign plan generated successfully.")


# ============================================================
# WEEK 1 PLAN
# ============================================================

state = st.session_state.state

if state:

    st.divider()
    st.subheader("2. Week 1 — Agent Plan")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="card">
            <h3>🎯 Target Audience</h3>
            <p>{state.get("target_audience", "Not specified")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
            <h3>📱 Channel Mix</h3>
            <p>{", ".join(state.get("channel_mix", []))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    posts = state.get("drafted_posts", [])

    st.subheader("Drafted Posts")

    for i, post in enumerate(posts, start=1):

        with st.container(border=True):

            st.markdown(f"### Post {i}")

            c1, c2 = st.columns([1, 3])

            with c1:
                st.write("**Channel**")
                st.write(post.get("channel", "Unknown"))

                st.write("**Time**")
                st.write(post.get("time_posted", "11:00"))

                st.write("**Hashtags**")
                st.write(
                    ", ".join(
                        "#" + str(x).lstrip("#")
                        for x in post.get("hashtags", [])
                    )
                )

            with c2:
                st.write("**Content**")
                st.write(post.get("content", ""))

                if post.get("creative_brief"):
                    st.write("**Creative Brief**")
                    st.write(post.get("creative_brief"))


    # ========================================================
    # HUMAN REVIEW
    # ========================================================

    st.divider()
    st.subheader("3. Human Review Gate")

    st.info(
        "Review the generated campaign above. "
        "Publishing happens only after human approval."
    )

    approve_col, reject_col = st.columns(2)

    with approve_col:

        if st.button(
            "✅ Approve & Publish Week 1",
            use_container_width=True
        ):

            try:

                with st.spinner("Publishing Week 1..."):

                    published = publisher_agent(state)

                st.session_state.week1_published = published

                with st.spinner("Analytics Agent is analyzing performance..."):

                    report = analytics_agent(
                        published,
                        "WEEK 1"
                    )

                st.session_state.week1_report = report

                st.success(
                    "Week 1 approved, published and analyzed."
                )

            except Exception as e:

                st.error(f"Publishing failed: {e}")

    with reject_col:

        if st.button(
            "❌ Reject Campaign",
            use_container_width=True
        ):

            st.warning(
                "Campaign rejected. Edit the brief and generate a new plan."
            )


# ============================================================
# WEEK 1 RESULTS
# ============================================================

report = st.session_state.week1_report

if report:

    st.divider()
    st.subheader("4. Week 1 Performance")

    published = st.session_state.week1_published or []

    total_views = sum(
        item.get("metrics", {}).get("views", 0)
        for item in published
    )

    total_likes = sum(
        item.get("metrics", {}).get("likes", 0)
        for item in published
    )

    total_comments = sum(
        item.get("metrics", {}).get("comments", 0)
        for item in published
    )

    total_saves = sum(
        item.get("metrics", {}).get("saves", 0)
        for item in published
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Views", f"{total_views:,}")

    with c2:
        st.metric("Likes", f"{total_likes:,}")

    with c3:
        st.metric("Comments", f"{total_comments:,}")

    with c4:
        st.metric("Saves", f"{total_saves:,}")


    st.subheader("Analytics Insights")

    insights = report.get("insights", [])
    if isinstance(insights, str):
        st.markdown(insights)
    else:
        for insight in insights:
            st.markdown(f"- {insight}")


    st.subheader("Recommendations")

    for rec in report.get("recommendations", []):
        st.markdown(f"**→** {rec}")


    # ========================================================
    # WEEK 2
    # ========================================================

    st.divider()
    st.subheader("5. Week 2 — Close the Loop")

    if st.button(
        "🔄 Generate Week 2 Improvement Plan",
        use_container_width=True
    ):

        with st.spinner("Creating Week 2 brief from Week 1 learning..."):

            week2_brief = create_week2_brief(
                report,
                brief
            )

        week2_initial_state = {
            "human_brief": week2_brief,
            "target_audience": "",
            "channel_mix": state.get("channel_mix", []),
            "drafted_posts": [],
            "feedback": ""
        }

        with st.spinner("Strategy Agent is planning Week 2..."):
            strategy2 = strategy_agent(week2_initial_state)

        week2_state = {
            **week2_initial_state,
            **strategy2
        }

        with st.spinner("Content Writer Agent is creating Week 2 posts..."):
            content2 = content_agent(week2_state)

        week2_state = {
            **week2_state,
            **content2
        }

        with st.spinner("Creative Agent is refining Week 2..."):
            creative2 = creative_agent(week2_state)

        week2_state = {
            **week2_state,
            **creative2
        }

        st.session_state.week2_state = week2_state

        st.success("Week 2 improvement plan generated.")


# ============================================================
# WEEK 2 PLAN + APPROVAL
# ============================================================

week2_state = st.session_state.week2_state

if week2_state:

    st.subheader("Week 2 Draft")

    st.info(
        "Week 2 uses Week 1 recommendations while keeping "
        "the campaign objective and audience consistent."
    )

    st.write(
        "**Target Audience:**",
        week2_state.get("target_audience", "")
    )

    st.write(
        "**Channels:**",
        ", ".join(week2_state.get("channel_mix", []))
    )

    for i, post in enumerate(
        week2_state.get("drafted_posts", []),
        start=1
    ):

        with st.container(border=True):

            st.markdown(f"### Week 2 Post {i}")

            st.write(
                f"**Channel:** {post.get('channel', 'Unknown')}"
            )

            st.write(
                f"**Content:** {post.get('content', '')}"
            )

            st.write(
                "**Hashtags:**",
                ", ".join(
                    "#" + str(x).lstrip("#")
                    for x in post.get("hashtags", [])
                )
            )


    if st.button(
        "✅ Approve & Publish Week 2",
        use_container_width=True
    ):

        try:

            with st.spinner("Publishing Week 2..."):

                published2 = publisher_agent(week2_state)

            st.session_state.week2_published = published2

            with st.spinner("Analyzing Week 2 performance..."):

                report2 = analytics_agent(
                    published2,
                    "WEEK 2"
                )

            st.session_state.week2_report = report2

            st.success(
                "Week 2 approved, published and analyzed."
            )

        except Exception as e:

            st.error(f"Week 2 publishing failed: {e}")


# ============================================================
# FINAL COMPARISON
# ============================================================

report2 = st.session_state.week2_report

if report2:

    st.divider()
    st.subheader("6. Week 1 → Week 2 Comparison")

    p1 = st.session_state.week1_published or []
    p2 = st.session_state.week2_published or []

    def totals(posts):
        return {
            "Views": sum(
                x.get("metrics", {}).get("views", 0)
                for x in posts
            ),
            "Likes": sum(
                x.get("metrics", {}).get("likes", 0)
                for x in posts
            ),
            "Comments": sum(
                x.get("metrics", {}).get("comments", 0)
                for x in posts
            ),
            "Saves": sum(
                x.get("metrics", {}).get("saves", 0)
                for x in posts
            )
        }

    week1_totals = totals(p1)
    week2_totals = totals(p2)

    comparison = pd.DataFrame({
        "Metric": list(week1_totals.keys()),
        "Week 1": list(week1_totals.values()),
        "Week 2": list(week2_totals.values())
    })

    comparison["Change"] = (
        comparison["Week 2"] -
        comparison["Week 1"]
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Week 2 Analytics")

    insights2 = report2.get("insights", [])
    if isinstance(insights2, str):
        st.markdown(insights2)
    else:
        for insight in insights2:
            st.markdown(f"- {insight}")

    st.subheader("Next Recommendations")

    for rec in report2.get("recommendations", []):
        st.markdown(f"**→** {rec}")

    st.success(
        "Closed-loop campaign complete: "
        "Week 1 → Analysis → Improvement → Week 2 → Analysis"
    )
