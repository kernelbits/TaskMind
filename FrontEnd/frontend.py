import streamlit as st
import requests
import pandas as pd

api_url = "http://127.0.0.1:8000/tasks"


st.title("TaskMind - ToDo App")


with st.form(key="task_form"):
    raw_task = st.text_input("Task : ",placeholder="Write a task to add...")
    submit_button = st.form_submit_button(label="Add Task")

if submit_button and raw_task:
    payload = {"original_text": raw_task}
    task_post_url = "http://127.0.0.1:8000/task"
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
        st.subheader("Tasks List")
        
        # Apply color styling to priority column
        def color_priority(val):
            if val == "High":
                return 'background-color: #ffcccc; color: #cc0000;'  # Red background
            elif val == "Medium":
                return 'background-color: #ffffcc; color: #cc9900;'  # Yellow background
            elif val == "Low":
                return 'background-color: #ccffcc; color: #009900;'  # Green background
            return ''
        
        styled_df = df.style.map(color_priority, subset=['priority'])
        st.dataframe(styled_df)
    else:
        st.info("No tasks added")
else:
    st.error("Failed to fetch tasks")


