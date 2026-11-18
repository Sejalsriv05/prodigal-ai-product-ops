from typing import TypedDict, List, Dict, Any
import json
import os
from ollama_wrapper import generate_json_response
import requests


# ============================================================
# 1. SHARED CAMPAIGN STATE
# ============================================================

class CampaignState(TypedDict):
    human_brief: str
    target_audience: str
    channel_mix: List[str]
    drafted_posts: List[Dict[str, Any]]
    feedback: str


# ============================================================
# 2. STRATEGY AGENT
# ============================================================

def strategy_agent(state: CampaignState) -> CampaignState:
    print("--- STRATEGY AGENT WORKING ---")

    prompt = f"""
    You are the Lead Strategist for a social media agency.

    Read the following human brief:
    "{state['human_brief']}"

    Based on this brief, output a JSON object with exactly two keys:

    1. "target_audience":
       A short string describing the target demographic.

    2. "channel_mix":
       A list of strings indicating which channels to use.
       Choose only from:
       "reel", "carousel", "static".
    """

    response = generate_json_response(prompt, model="llama3")

    if response:
        return {
            "target_audience": response.get(
                "target_audience",
                "General Audience"
            ),
            "channel_mix": response.get(
                "channel_mix",
                ["static"]
            )
        }

    return {
        "target_audience": "General Audience",
        "channel_mix": ["static"]
    }


# ============================================================
# 3. CONTENT WRITER AGENT
# ============================================================

def content_agent(state: CampaignState) -> CampaignState:
    print("--- CONTENT WRITER AGENT WORKING ---")

    prompt = f"""
    You are the Content Writer for a social media agency.

    Campaign Brief:
    "{state['human_brief']}"

    Target Audience:
    "{state['target_audience']}"

    Channels to use:
    {state['channel_mix']}

    Write exactly one post for EACH channel in the channel mix.

    Output a JSON object with a single key:
    "drafted_posts"

    Each object must contain:
    - "channel"
    - "content"
    - "hashtags"

    Hashtags must contain 3-5 strings.

    Keep the tone playful and do not over-promise.
    """

    response = generate_json_response(prompt, model="llama3")

    if response and "drafted_posts" in response:
        posts = response["drafted_posts"]
        for post in posts:
            import re
            hashtags = post.get("hashtags", [])
            if isinstance(hashtags, str):
                hashtags = re.findall(r"#([A-Za-z0-9_]+)", hashtags)
            elif isinstance(hashtags, list):
                hashtags = [str(h).lstrip("#").strip() for h in hashtags if str(h).strip() and str(h).strip() != "#"]
                if len(hashtags) > 5:
                    hashtags = hashtags[:5]
            else:
                hashtags = []
            if not hashtags:
                hashtags = re.findall(r"#([A-Za-z0-9_]+)", post.get("content", ""))[:5]
            post["hashtags"] = hashtags
        return {
            "drafted_posts": posts
        }

    return {
        "drafted_posts": []
    }


# ============================================================
# 4. CREATIVE AGENT
# ============================================================

def creative_agent(state: CampaignState) -> CampaignState:
    print("--- CREATIVE AGENT WORKING ---")

    posts = state.get("drafted_posts", [])

    if not posts:
        return {
            "drafted_posts": []
        }

    prompt = f"""
    You are a Creative Director specializing in 3D product rendering.

    Here are the drafted social media posts:

    {json.dumps(posts)}

    For each post, write a highly descriptive text brief
    for the 3D artists to model the asset.

    Focus on:
    - lighting
    - rendering style
    - camera angles
    - texturing details

    Output a JSON object with a key:
    "drafted_posts"

    Keep the original:
    - channel
    - content
    - hashtags

    Add:
    - creative_brief
    """

    response = generate_json_response(prompt, model="llama3")

    if response and "drafted_posts" in response:
        posts = response["drafted_posts"]
        for post in posts:
            import re
            hashtags = post.get("hashtags", [])
            if isinstance(hashtags, str):
                hashtags = re.findall(r"#([A-Za-z0-9_]+)", hashtags)
            elif isinstance(hashtags, list):
                hashtags = [str(h).lstrip("#").strip() for h in hashtags if str(h).strip() and str(h).strip() != "#"]
                if len(hashtags) > 5:
                    hashtags = hashtags[:5]
            else:
                hashtags = []
            if not hashtags:
                hashtags = re.findall(r"#([A-Za-z0-9_]+)", post.get("content", ""))[:5]
            post["hashtags"] = hashtags
        return {
            "drafted_posts": posts
        }

    return {
        "drafted_posts": posts
    }


# ============================================================
# 5. PUBLISHER AGENT
# ============================================================

def publisher_agent(state: CampaignState):
    print("\n--- PUBLISHER AGENT WORKING ---")

    published_results = []

    api_base_url = os.getenv("API_BASE_URL")
    if not api_base_url:
        try:
            import streamlit as st
            api_base_url = st.secrets["API_BASE_URL"]
        except Exception:
            api_base_url = "http"+chr(58)+chr(47)+chr(47)+"localhost:8000"

    for post in state.get("drafted_posts", []):

        payload = {
            "channel": post["channel"],
            "content": post["content"],
            "creative_brief": json.dumps(post.get("creative_brief", "No brief provided.")) if isinstance(post.get("creative_brief"), dict) else post.get("creative_brief", "No brief provided."),
            "hashtags": post.get("hashtags", []),
            "time_posted": "11:00"
        }

        try:
            response = requests.post(
                api_base_url.rstrip("/") + "/posts/publish",
                json=payload
            )

            response.raise_for_status()

            result = response.json()

            print(
                f"✅ Successfully published to "
                f"{post['channel'].upper()}!"
            )

            print(
                f"📊 Simulated Metrics Generated: "
                f"{result['metrics']}"
            )

            result["channel"] = post["channel"]
            result["content"] = post["content"]
            result["hashtags"] = post.get("hashtags", [])
            result["time_posted"] = payload["time_posted"]
            published_results.append(result)

        except requests.exceptions.RequestException as e:

            print(
                f"❌ Failed to publish to "
                f"{post['channel']}: {e}"
            )

    return published_results


# ============================================================
# 6. ANALYTICS AGENT
# ============================================================

def analytics_agent(
    published_results,
    week_label="WEEK 1"
):

    print(
        f"\n--- ANALYTICS AGENT WORKING "
        f"({week_label}) ---"
    )

    if not published_results:
        print("No published campaign data found.")

        return {
            "totals": {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "saves": 0
            },
            "averages": {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "saves": 0
            },
            "insights": "",
            "recommendations": []
        }

    # --------------------------------------------------------
    # Deterministic calculations
    # --------------------------------------------------------

    total_views = sum(
        item["metrics"]["views"]
        for item in published_results
    )

    total_likes = sum(
        item["metrics"]["likes"]
        for item in published_results
    )

    total_comments = sum(
        item["metrics"]["comments"]
        for item in published_results
    )

    total_saves = sum(
        item["metrics"]["saves"]
        for item in published_results
    )

    post_count = len(published_results)

    avg_views = round(
        total_views / post_count,
        2
    )

    avg_likes = round(
        total_likes / post_count,
        2
    )

    avg_comments = round(
        total_comments / post_count,
        2
    )

    avg_saves = round(
        total_saves / post_count,
        2
    )

    # --------------------------------------------------------
    # Give only current campaign data to the LLM
    # --------------------------------------------------------

    campaign_data = []

    for item in published_results:

        campaign_data.append({
            "post_id": item["post_id"],
            "channel": item.get("channel", "unknown"),
            "content_length_words": len(item.get("content", "").split()),
            "hashtag_count": len(item.get("hashtags", [])),
            "time_posted": item.get("time_posted", "unknown"),
            "content": item.get("content", ""),
            "metrics": item["metrics"]
        })

    channel_values = [item.get("channel", "unknown") for item in published_results]
    hashtag_values = [item.get("hashtag_count", 0) for item in campaign_data]
    time_values = [item.get("time_posted", "unknown") for item in campaign_data]
    word_values = [item.get("content_length_words", 0) for item in campaign_data]

    evidence_summary = f"""
    Evidence availability:
    - Channels observed: {sorted(set(channel_values))}
    - Hashtag counts observed: {sorted(set(hashtag_values))}
    - Posting times observed: {sorted(set(time_values))}
    - Content word counts observed: {sorted(set(word_values))}

    Only analyze the effect of a variable when there is meaningful variation
    in that variable across the posts. If all posts have the same value,
    explicitly say there is insufficient evidence to evaluate that variable.
    """

    prompt = f"""
    You are the Lead Data Analyst for a social media agency.

    Analyze ONLY this campaign performance data:

    {json.dumps(campaign_data)}

    {evidence_summary}

    Deterministic campaign totals:

    Views: {total_views}
    Likes: {total_likes}
    Comments: {total_comments}
    Saves: {total_saves}

    Average per post:

    Views: {avg_views}
    Likes: {avg_likes}
    Comments: {avg_comments}
    Saves: {avg_saves}

    Identify meaningful performance patterns by comparing posts.

    SINGLE-POST OVERRIDE:
    If there is only 1 post, the insights MUST begin by stating that only one post was observed and that there is insufficient evidence for channel or feature comparisons. Describe only the observed metrics and content. Do NOT use words such as "dominated", "best", "worst", "correlation", "related", or "strongest" to compare features when only one post exists.

    IMPORTANT EVIDENCE RULES:
    - There are {post_count} posts in this reporting period.
    - If there is only 1 post, do NOT make comparative claims about channels,
      content length, hashtag count, posting time, or content features.
    - With only 1 post, describe the observed performance and state that
      there is insufficient evidence to determine what caused it.
    - With multiple posts, compare patterns only when the data supports them.
    - Never claim that a feature caused a metric to increase or decrease.
    - Recommendations must be directly supported by observed evidence.
    - If there is only 1 post, recommendations must focus on what to test next,
      not on claiming that a channel, hashtag, content length, or posting time is better.
    - Do not recommend increasing or changing a variable unless there is evidence
      in the available data that this variable may matter.
    - A variable with only one observed value MUST NOT be used as a recommendation.
      For example, if all posts have the same posting time or hashtag count,
      do not recommend changing that variable.
    - Do not infer that longer content is better merely because a few long posts
      have high metrics. Require repeated evidence across multiple posts.
    - Prefer recommendations based on channel-level performance differences,
      repeated content patterns, or clear week-over-week improvements.
    - If fewer than 3 evidence-backed changes exist, use recommendations framed
      as controlled tests of variables that have enough variation, rather than
      asserting that one option is better.

    Pay special attention to:
    - Which channel performed best and worst.
    - Whether shorter or longer content performed better.
    - Whether hashtag count appears related to performance.
    - Whether posting time appears related to performance.
    - Which engagement metric (likes, comments, or saves) is strongest.
    - Specific content patterns visible in the actual post text.

    Only claim a relationship when the provided data supports it.
    Do not claim causation from a small sample.

    Output JSON with exactly two keys:

    1. "insights":
       A concise paragraph explaining the strongest evidence-based patterns.

    2. "recommendations":
       A list of exactly 3 concrete, actionable changes for the next week.
       Each recommendation must be directly connected to an observed pattern.
       Do not recommend reducing a metric such as views, likes, comments, or saves.

    Do not invent metrics.
    Do not invent data that is not present.
    """

    response = generate_json_response(
        prompt,
        model="llama3"
    )

    # --------------------------------------------------------
    # Print report
    # --------------------------------------------------------

    print(
        f"\n📈 {week_label} PERFORMANCE REPORT 📈"
    )

    print(f"Total Posts: {post_count}")
    print(f"Total Views: {total_views}")
    print(f"Total Likes: {total_likes}")
    print(f"Total Comments: {total_comments}")
    print(f"Total Saves: {total_saves}")

    print(
        f"Average Views/Post: {avg_views}"
    )

    print(
        f"Average Likes/Post: {avg_likes}"
    )

    print(
        f"Average Comments/Post: {avg_comments}"
    )

    print(
        f"Average Saves/Post: {avg_saves}"
    )

    if response:

        print(
            f"\nInsights: "
            f"{response.get('insights', 'No insights generated.')}"
        )

        # --------------------------------------------------------
        # Deterministic evidence-based recommendations
        # --------------------------------------------------------
        recommendations = []

        channel_groups = {}
        for item in campaign_data:
            channel = item.get("channel", "unknown").lower()
            channel_groups.setdefault(channel, []).append(item["metrics"]["views"])

        if len(channel_groups) >= 2:
            channel_avg = {
                channel: round(sum(values) / len(values), 2)
                for channel, values in channel_groups.items()
            }
            best_channel = max(channel_avg, key=channel_avg.get)
            worst_channel = min(channel_avg, key=channel_avg.get)
            if channel_avg[best_channel] > channel_avg[worst_channel]:
                recommendations.append(
                    f"Prioritize {best_channel.upper()} content next week, while retaining some {worst_channel.upper()} content for comparison."
                )

        if len(set(hashtag_values)) >= 2 and len(campaign_data) >= 4:
            recommendations.append(
                "Continue testing different hashtag counts or combinations and compare their performance across multiple posts."
            )

        if len(set(word_values)) >= 2 and len(campaign_data) >= 4:
            recommendations.append(
                "Test different content lengths across multiple posts before deciding whether shorter or longer copy performs better."
            )

        if len(set(time_values)) >= 2 and len(campaign_data) >= 4:
            recommendations.append(
                "Compare different posting times across multiple posts to identify whether timing is associated with performance."
            )

        # Fill remaining slots with safe controlled tests rather than unsupported claims.
        safe_tests = [
            "Repeat the strongest-performing content pattern with multiple posts to confirm that the result is reproducible.",
            "Keep the target audience and campaign objective constant while testing one execution variable at a time.",
            "Use next week's results to validate whether the observed performance improvement is sustained."
        ]

        for test in safe_tests:
            if len(recommendations) >= 3:
                break
            recommendations.append(test)

        recommendations = recommendations[:3]

        print(
            "\nRecommendations for Next Week:"
        )

        for rec in recommendations:
            print(f" - {rec}")

        return {
            "totals": {
                "views": total_views,
                "likes": total_likes,
                "comments": total_comments,
                "saves": total_saves
            },
            "averages": {
                "views": avg_views,
                "likes": avg_likes,
                "comments": avg_comments,
                "saves": avg_saves
            },
            "insights": response.get(
                "insights",
                ""
            ),
            "recommendations": recommendations
        }

    return {
        "totals": {
            "views": total_views,
            "likes": total_likes,
            "comments": total_comments,
            "saves": total_saves
        },
        "averages": {
            "views": avg_views,
            "likes": avg_likes,
            "comments": avg_comments,
            "saves": avg_saves
        },
        "insights": "",
        "recommendations": []
    }


# ============================================================
# 7. WEEK 2 BRIEF GENERATOR
# ============================================================

def create_week2_brief(
    week1_report,
    original_brief
):

    recommendations = week1_report.get(
        "recommendations",
        []
    )

    recommendation_text = "\n".join(
        f"- {rec}"
        for rec in recommendations
    )

    return f"""
Original campaign brief:
{original_brief}

Week 1 performance recommendations:
{recommendation_text}

Create the Week 2 campaign brief by improving the original campaign,
not replacing its objective.

Apply the Week 1 recommendations as concrete execution changes.
Prioritize recommendations that are directly supported by Week 1 data.
Do not introduce unrelated campaign goals.
Do not intentionally reduce views, likes, comments, or saves.
Keep the same target audience.

Week 2 should test improvements based on Week 1 learning so that
Week 2 performance can be compared against Week 1.
"""


# ============================================================
# 8. DISPLAY CAMPAIGN FOR HUMAN APPROVAL
# ============================================================

def human_review(state):

    print("\n==================================")
    print("       HUMAN REVIEW REQUIRED")
    print("==================================")

    for idx, post in enumerate(
        state["drafted_posts"]
    ):

        print(
            f"\n--- Post {idx + 1} "
            f"({post['channel'].upper()}) ---"
        )

        print(
            f"Content: {post['content']}"
        )

        print(
            f"Hashtags: "
            f"{', '.join(post.get('hashtags', []))}"
        )

        print(
            f"Visual Brief: "
            f"{post.get('creative_brief', '')}"
        )

    return input(
        "\nDo you approve these posts "
        "for publishing? (yes/no): "
    )


# ============================================================
# 9. FULL WEEK 1 + WEEK 2 PIPELINE
# ============================================================

def run_campaign(original_brief):

    initial_state = {
        "human_brief": original_brief,
        "target_audience": "",
        "channel_mix": [],
        "drafted_posts": [],
        "feedback": ""
    }

    # ========================================================
    # WEEK 1
    # ========================================================

    state_after_strategy = strategy_agent(initial_state)
    current_state = {**initial_state, **state_after_strategy}

    state_after_content = content_agent(current_state)
    current_state = {**current_state, **state_after_content}

    state_after_creative = creative_agent(current_state)
    current_state = {**current_state, **state_after_creative}

    return current_state


if __name__ == "__main__":

    original_brief = (
        "We are launching a budget espresso "
        "machine for students. Run a short "
        "awareness campaign."
    )

    initial_state = {
        "human_brief": original_brief,
        "target_audience": "",
        "channel_mix": [],
        "drafted_posts": [],
        "feedback": ""
    }

    # ========================================================
    # WEEK 1
    # ========================================================

    print("\n\n")
    print("########################################")
    print("#              WEEK 1                  #")
    print("########################################")

    # Strategy
    state_after_strategy = strategy_agent(
        initial_state
    )

    current_state = {
        **initial_state,
        **state_after_strategy
    }

    # Content
    state_after_content = content_agent(
        current_state
    )

    current_state = {
        **current_state,
        **state_after_content
    }

    # Creative
    state_after_creative = creative_agent(
        current_state
    )

    current_state = {
        **current_state,
        **state_after_creative
    }

    # Human approval
    approval = human_review(
        current_state
    )

    if approval.lower() not in ["yes", "y"]:

        print(
            "\nCampaign rejected by human "
            "operator. Halting pipeline."
        )

        exit()

    # Publisher
    print(
        "\nCampaign approved! "
        "Handing off to Publisher Agent..."
    )

    published_results_week1 = publisher_agent(
        current_state
    )

    # Analytics
    week1_report = analytics_agent(
        published_results_week1,
        "WEEK 1"
    )


    # ========================================================
    # WEEK 2
    # ========================================================

    print("\n\n")
    print("########################################")
    print("#              WEEK 2                  #")
    print("########################################")

    print(
        "\n🔄 Feeding Week 1 recommendations "
        "back into the campaign..."
    )

    # Create improved brief
    week2_brief = create_week2_brief(
        week1_report,
        original_brief
    )

    print(
        "\n📝 WEEK 2 BRIEF CREATED:"
    )

    print(week2_brief)

    # --------------------------------------------------------
    # Week 2 Strategy
    # --------------------------------------------------------

    week2_initial_state = {
        "human_brief": week2_brief,
        "target_audience": "",
        "channel_mix": current_state["channel_mix"],
        "drafted_posts": [],
        "feedback": ""
    }

    state_after_strategy_w2 = strategy_agent(
        week2_initial_state
    )

    week2_state = {
        **week2_initial_state,
        **state_after_strategy_w2
    }

    # --------------------------------------------------------
    # Week 2 Content
    # --------------------------------------------------------

    state_after_content_w2 = content_agent(
        week2_state
    )

    week2_state = {
        **week2_state,
        **state_after_content_w2
    }

    # --------------------------------------------------------
    # Week 2 Creative
    # --------------------------------------------------------

    state_after_creative_w2 = creative_agent(
        week2_state
    )

    week2_state = {
        **week2_state,
        **state_after_creative_w2
    }

    # --------------------------------------------------------
    # Week 2 Human Approval
    # --------------------------------------------------------

    approval_w2 = human_review(
        week2_state
    )

    if approval_w2.lower() not in ["yes", "y"]:

        print(
            "\nWeek 2 campaign rejected by "
            "human operator."
        )

        exit()

    # --------------------------------------------------------
    # Week 2 Publisher
    # --------------------------------------------------------

    print(
        "\nWeek 2 campaign approved! "
        "Handing off to Publisher Agent..."
    )

    published_results_week2 = publisher_agent(
        week2_state
    )

    # --------------------------------------------------------
    # Week 2 Analytics
    # --------------------------------------------------------

    week2_report = analytics_agent(
        published_results_week2,
        "WEEK 2"
    )


    # ========================================================
    # BEFORE / AFTER COMPARISON
    # ========================================================

    print("\n\n")
    print("########################################")
    print("#        WEEK 1 vs WEEK 2              #")
    print("########################################")

    w1 = week1_report["totals"]
    w2 = week2_report["totals"]

    print(
        f"\nViews:    {w1['views']} → {w2['views']}"
    )

    print(
        f"Likes:    {w1['likes']} → {w2['likes']}"
    )

    print(
        f"Comments: {w1['comments']} → {w2['comments']}"
    )

    print(
        f"Saves:    {w1['saves']} → {w2['saves']}"
    )

    print("\n📊 CHANGE FROM WEEK 1 TO WEEK 2")

    print(
        f"Views change: "
        f"{w2['views'] - w1['views']:+d}"
    )

    print(
        f"Likes change: "
        f"{w2['likes'] - w1['likes']:+d}"
    )

    print(
        f"Comments change: "
        f"{w2['comments'] - w1['comments']:+d}"
    )

    print(
        f"Saves change: "
        f"{w2['saves'] - w1['saves']:+d}"
    )

    print(
        "\n✅ Closed-loop campaign execution complete."
    )

