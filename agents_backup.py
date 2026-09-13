from typing import TypedDict, List, Dict, Any
import json
# We import the Ollama wrapper we wrote earlier!
# Make sure your previous wrapper script is saved as 'ollama_wrapper.py'
from ollama_wrapper import generate_json_response 
import sqlite3
import requests # Ensure this is at the top of your file

# 1. Define the Shared Memory (State)
class CampaignState(TypedDict):
    human_brief: str
    target_audience: str
    channel_mix: List[str]
    drafted_posts: List[Dict[str, Any]]
    feedback: str

# 2. The Strategy Agent Function
def strategy_agent(state: CampaignState) -> CampaignState:
    print("--- STRATEGY AGENT WORKING ---")
    
    prompt = f"""
    You are the Lead Strategist for a social media agency.
    Read the following human brief: "{state['human_brief']}"
    
    Based on this brief, output a JSON object with exactly two keys:
    1. "target_audience": A short string describing the target demographic.
    2. "channel_mix": A list of strings indicating which channels to use (choose from: "reel", "carousel", "static").
    """
    
    # Call the local model using your wrapper
    response = generate_json_response(prompt, model="llama3")
    
    # Update the state with the agent's decisions
    if response:
        return {
            "target_audience": response.get("target_audience", "General Audience"),
            "channel_mix": response.get("channel_mix", ["static"])
        }
    else:
        return {"target_audience": "Error", "channel_mix": []}

# 3. The Content Writer Agent
def content_agent(state: CampaignState) -> CampaignState:
    print("--- CONTENT WRITER AGENT WORKING ---")
    
    prompt = f"""
    You are the Content Writer for a social media agency.
    Campaign Brief: "{state['human_brief']}"
    Target Audience: "{state['target_audience']}"
    Channels to use: {state['channel_mix']}
    
    Write exactly one post for EACH channel in the channel mix. 
    Output a JSON object with a single key "drafted_posts" containing a list of objects.
    Each object must have: "channel" (string), "content" (string - the post copy), and "hashtags" (list of 3-5 strings).
    Keep the tone playful and do not over-promise.
    """
    
    response = generate_json_response(prompt, model="llama3")
    
    if response and "drafted_posts" in response:
        return {"drafted_posts": response["drafted_posts"]}
    return {"drafted_posts": []}

# 4. The Creative Agent
def creative_agent(state: CampaignState) -> CampaignState:
    print("--- CREATIVE AGENT WORKING ---")
    
    posts = state.get("drafted_posts", [])
    if not posts:
        return {"drafted_posts": []}

    prompt = f"""
    You are a Creative Director specializing in 3D product rendering.
    Here are the drafted social media posts: {json.dumps(posts)}
    
    For each post, write a highly descriptive text brief for the 3D artists to model the asset. 
    Focus on lighting, rendering style (e.g., cinematic, studio), camera angles, and texturing details.
    
    Output a JSON object with a key "drafted_posts" containing the updated list of posts. 
    Keep the original "channel", "content", and "hashtags", but add a new key "creative_brief" (string) to each post.
    """
    
    response = generate_json_response(prompt, model="llama3")
    
    if response and "drafted_posts" in response:
        return {"drafted_posts": response["drafted_posts"]}
    
    return {"drafted_posts": posts} # Fallback to original posts if it fails

# 5. The Publisher Agent
def publisher_agent(state: CampaignState):
    print("\n--- PUBLISHER AGENT WORKING ---")
    published_results = []
    
    for post in state.get("drafted_posts", []):
        # Format the payload to match the PostCreate schema in our FastAPI backend
        payload = {
            "channel": post["channel"],
            "content": post["content"],
            "creative_brief": post.get("creative_brief", "No brief provided."),
            "hashtags": post.get("hashtags", []),
            "time_posted": "11:00" # We hardcode 11:00 to trigger the 1.25x engagement boost hidden rule!
        }
        
        try:
            # Send the HTTP POST request to your mock platform
            response = requests.post("http://localhost:8000/posts/publish", json=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Successfully published to {post['channel'].upper()}!")
            print(f"📊 Simulated Metrics Generated: {result['metrics']}")
            published_results.append(result)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to publish to {post['channel']}: {e}")
            
    return published_results

# 6. The Analytics Agent
def analytics_agent():
    print("\n--- ANALYTICS AGENT WORKING ---")
    
    # 1. Connect to the database and fetch the campaign data
    conn = sqlite3.connect("mock_instagram.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT channel, content, views, likes, comments, saves FROM posts")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No data found in the database. Run a campaign first!")
        return

    # Convert rows to a list of dictionaries so the LLM can read it
    campaign_data = [dict(row) for row in rows]
    
    # 2. Prompt the Analyst
    prompt = f"""
    You are the Lead Data Analyst for a social media agency.
    Here is the performance data from our first week's campaign: {json.dumps(campaign_data)}
    
    Your job is to analyze this data and find patterns. Compare the performance across the different channels (e.g., Views vs. Saves). 
    
    Output a JSON object with exactly two keys:
    1. "insights": A short paragraph explaining what performed well and why you think it happened.
    2. "recommendations": A list of 2 or 3 concrete, specific changes for next week's campaign (e.g., text length, channel strategy, calls to action).
    """
    
    response = generate_json_response(prompt, model="llama3")
    
    if response:
        print("\n📈 WEEKLY PERFORMANCE REPORT 📈")
        print(f"Insights: {response.get('insights')}")
        print("Recommendations for Next Week:")
        for rec in response.get("recommendations", []):
            print(f" - {rec}")
    else:
        print("Analytics Agent failed to generate a report.")


# --- Full Pipeline Execution ---
if __name__ == "__main__":
    initial_state = {
        "human_brief": "We are launching a budget espresso machine for students. Run a short awareness campaign.",
        "target_audience": "",
        "channel_mix": [],
        "drafted_posts": [],
        "feedback": ""
    }

    # 1. Strategy Agent
    state_after_strategy = strategy_agent(initial_state)
    current_state = {**initial_state, **state_after_strategy}

    # 2. Content Writer Agent
    state_after_content = content_agent(current_state)
    current_state = {**current_state, **state_after_content}

    # 3. Creative Agent
    state_after_creative = creative_agent(current_state)
    current_state = {**current_state, **state_after_creative}

    # 4. Human Approval Gate
    print("\n==================================")
    print("       HUMAN REVIEW REQUIRED")
    print("==================================")

    for idx, post in enumerate(current_state["drafted_posts"]):
        print(f"\n--- Post {idx + 1} ({post['channel'].upper()}) ---")
        print(f"Content: {post['content']}")
        print(f"Hashtags: {', '.join(post.get('hashtags', []))}")
        print(f"Visual Brief: {post.get('creative_brief', '')}")

    approval = input("\nDo you approve these posts for publishing? (yes/no): ")

    # 5. Publisher Agent
    if approval.lower() in ["yes", "y"]:
        print("\nCampaign approved! Handing off to Publisher Agent...")
        publisher_agent(current_state)

        # 6. Analytics Agent
        analytics_agent()
    else:
        print("\nCampaign rejected by human operator. Halting pipeline.")

# --- Quick Test ---
# --- Quick Test ---
# # --- Full Pipeline Execution ---
# if __name__ == "__main__":
#     initial_state = {
#         "human_brief": "We are launching a budget espresso machine for students. Run a short awareness campaign.",
#         "target_audience": "",
#         "channel_mix": [],
#         "drafted_posts": [],
#         "feedback": ""
#     }
    
#     # 1. Run Strategy
#     state_after_strategy = strategy_agent(initial_state)
#     current_state = {**initial_state, **state_after_strategy}
    
#     # 2. Run Content Writer
#     state_after_content = content_agent(current_state)
#     current_state = {**current_state, **state_after_content}
    
#     # 3. Run Creative
#     state_after_creative = creative_agent(current_state)
#     current_state = {**current_state, **state_after_creative}
    
#     # 4. Human Approval Gate
#     print("\n==================================")
#     print("      HUMAN REVIEW REQUIRED       ")
#     print("==================================")
    
#     for idx, post in enumerate(current_state["drafted_posts"]):
#         print(f"\n--- Post {idx + 1} ({post['channel'].upper()}) ---")
#         print(f"Content: {post['content']}")
#         print(f"Hashtags: {', '.join(post.get('hashtags', []))}")
#         print(f"Visual Brief: {post.get('creative_brief', '')}")

#     # The system pauses here and waits for your keyboard input
#     approval = input("\nDo you approve these posts for publishing? (yes/no): ")

#     # 5. Conditional Publishing
#     if approval.lower() in ["yes", "y"]:
#         print("\nCampaign approved! Handing off to Publisher Agent...")
#         publisher_agent(current_state)
#     else:
#         print("\nCampaign rejected by human operator. Halting pipeline.")
#         # In a fully mapped LangGraph loop, a rejection here would route back to the Strategy or Content agent.
