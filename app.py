import os
import streamlit as st
import openai
from moviepy.editor import VideoFileClip

# Ensure the specified directory exists, creating it if necessary
def ensure_directory_exists(directory):
    """Create the directory if it doesn't exist to store transcripts."""
    if not os.path.exists(directory):
        os.makedirs(directory)

# Extract audio from video and save as an MP3 file
@st.cache(allow_output_mutation=True)
def extract_audio(video_file_path, output_audio_path):
    """Extracts audio from video files to facilitate audio transcription."""
    video = VideoFileClip(video_file_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path, codec='mp3')
    audio.close()
    video.close()

# Transcribe audio to text using OpenAI's Whisper model
@st.cache(allow_output_mutation=True)
def transcribe(audio_file_path, api_key):
    """Transcribe audio to text for further processing and analysis in Scrum planning."""
    try:
        openai.api_key = api_key
        with open(audio_file_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
            return transcription['text'] if 'text' in transcription else "No transcript available."
    except Exception as e:
        st.error(f"Failed to transcribe audio: {str(e)}")
        return ""

# Summarize transcription focusing on actionable insights for Scrum planning
@st.cache(allow_output_mutation=True)
def summarize_transcription(transcription, context, api_key):
    """Generates a concise summary and actionable points from the transcription tailored for Scrum teams."""
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": f"Convert this detailed transcript into a concise format suitable for Scrum: identify key user stories, tasks, and acceptance criteria that align with the project goals. Context: {context}."},
        {"role": "user", "content": transcription}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response['choices'][0]['message']['content'] if response else "Summarization failed."

# Generate epics and tasks based on summarized content
def generate_epics_and_tasks(summary, context=""):
    """From the summary, derive epics and tasks that can be added to Scrum boards, including dependencies and story points."""
    messages = [
        {"role": "system", "content": "Generate structured Scrum epics and tasks from summary including dependencies and story points."},
        {"role": "user", "content": summary}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response['choices'][0]['message']['content'].strip().split('\n') if response else ["Breakdown generation failed."]





def display_artifacts(breakdown_items):
    """Display epics and tasks in a structured table format with updated parsing logic."""
    import pandas as pd
    data = {
        "Epic": [],
        "Story Points": [],
        "Tasks": [],
        "Dependencies": []
    }
    
    current_epic = ""
    story_points = ""
    tasks = []
    dependencies = []
    
    for item in breakdown_items:
        if 'Epic' in item:  # Starts a new epic
            if current_epic:  # Save previous epic data before starting new
                data["Epic"].append(current_epic)
                data["Story Points"].append(story_points)
                data["Tasks"].append(", ".join(tasks))
                data["Dependencies"].append(", ".join(dependencies))
            current_epic = item.split(":")[1].strip()
            story_points = ""
            tasks = []
            dependencies = []
        elif '- Task' in item:  # Parses tasks and their story points
            task_detail = item.split(":")[1].strip()
            task_name_points = task_detail.rsplit("(", 1)
            if len(task_name_points) == 2:
                task_name, points = task_name_points
                tasks.append(task_name.strip())
                story_points += points.rstrip(" story points)").strip() + ", "
            else:
                # Handle unexpected format
                print("Unexpected format for task:", item)
        elif 'depends on Task' in item:  # Parses dependencies
            dependency_detail = item.split(":")[1].strip()
            dependencies.append(dependency_detail)

    # Save the last epic's data
    if current_epic:
        data["Epic"].append(current_epic)
        data["Story Points"].append(story_points)
        data["Tasks"].append(", ".join(tasks))
        data["Dependencies"].append(", ".join(dependencies))

    df = pd.DataFrame(data)
    st.table(df)  # Display the table







def main():
    st.set_page_config(layout="wide")
    st.title("From Audio to JIRA and Confluence")
    st.subheader("Audio and Video Upload and Transcription App for Scrum Teams")
    temp_dir = r'C:\Temp\transcripts'
    ensure_directory_exists(temp_dir)
    api_key = st.text_input("Enter your OpenAI API key:", type="password")

    # Define column widths
    cols = st.columns(3)

    # Upload and Transcribe for Scrum Documentation
    with cols[0]:
        with st.expander("Upload and Transcribe"):
            uploaded_file = st.file_uploader("Choose a file", type=["mp3", "mp4", "m4a"])
            if uploaded_file is not None:
                file_name = os.path.join(temp_dir, uploaded_file.name)
                file_type = uploaded_file.type.split('/')[1]
                with open(file_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if file_type == "mp4":
                    audio_file_path = file_name.split('.')[0] + '.mp3'
                    extract_audio(file_name, audio_file_path)
                    st.video(file_name)
                else:
                    audio_file_path = file_name
                    st.audio(file_name, format=f'audio/{file_type}')
                
                if st.button("Start Transcription"):
                    transcription = transcribe(audio_file_path, api_key)
                    st.text_area("Transcription:", value=transcription, height=200)
                    st.session_state.transcription = transcription

    # Summarize Transcript for Scrum Meetings
    with cols[1]:
        if 'transcription' in st.session_state:
            with st.expander("Summarize for Scrum Meeting"):
                summarization_context = st.text_input("Provide context for tailored summarization:")
                if st.button("Summarize"):
                    summary = summarize_transcription(st.session_state.transcription, summarization_context, api_key)
                    st.text_area("Summary:", value=summary, height=200)
                    st.session_state.summary = summary

    # Breakdown into Scrum Epics and Tasks
    with cols[2]:
        if 'summary' in st.session_state:
            with st.expander("Generate Scrum Artifacts"):
                context = st.text_input("Context for detailed breakdown:")
                if st.button("Generate Breakdown"):
                    breakdown_items = generate_epics_and_tasks(st.session_state.summary, context)
                    st.write("Generated Scrum Artifacts:")
                    display_artifacts(breakdown_items)

    # Cleanup resources
    if uploaded_file is not None:
        os.remove(file_name)
        if file_type == "mp4":
            os.remove(audio_file_path)

if __name__ == "__main__":
    main()
