import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL","http://backend:8000")
api_url = f"{BACKEND_URL}/tasks"
task_post_url = f"{BACKEND_URL}/task"

# Set page config for wide layout
st.set_page_config(layout="wide", page_title="TaskMind - ToDo App")

st.title("TaskMind - ToDo App")

with st.form(key="task_form"):
    raw_task = st.text_input("Task : ", placeholder="Write a task to add...")
    submit_button = st.form_submit_button(label="Add Task")

if submit_button and raw_task:
    payload = {"original_text": raw_task}
    response = requests.post(url=task_post_url, json=payload)
    if response.status_code == 200:
        st.success(f"Task added : {response.json()['title']}")
    else:
        st.error("Task failed to add")

tasks_response = requests.get(url=api_url)
if tasks_response.status_code == 200:
    tasks = tasks_response.json()
    if tasks:
        df = pd.DataFrame(tasks)

        # Convert priority to string if needed
        if 'priority' in df.columns:
            df['priority'] = df['priority'].astype(str)

        st.subheader("Tasks List")


        # Apply color styling to priority column
        def color_priority(val):
            val_str = str(val)
            if "High" in val_str:
                return 'background-color: #ffcccc; color: #cc0000;'
            elif "Medium" in val_str:
                return 'background-color: #ffffcc; color: #cc9900;'
            elif "Low" in val_str:
                return 'background-color:  #ccffcc; color: #009900;'
            return ''


        styled_df = df.style.applymap(color_priority, subset=['priority'])

        # Make table use full container width and add height
        st.dataframe(styled_df, use_container_width=True, height=600)
    else:
        st.info("No tasks added")
else:
    st.error("Failed to fetch tasks")