import streamlit as st


st.title("TaskMind")

with st.form("add_task"):
    task_text = st.text_input("New Task",placeholder="Add a new task ...")
    submitted = st.form_submit_button("Add")