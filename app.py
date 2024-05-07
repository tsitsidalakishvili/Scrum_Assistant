import os
import streamlit as st
import openai
import plotly.graph_objects as go  # Import Plotly for graph visualization
from moviepy.editor import VideoFileClip

# Function to ensure the specified directory exists
def ensure_directory_exists(directory):
    """Ensure that the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

@st.cache(allow_output_mutation=True)
def extract_audio(video_file_path, output_audio_path):
    """Extract audio from a video file and save it as an MP3 file."""
    video = VideoFileClip(video_file_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path, codec='mp3')
    audio.close()
    video.close()

@st.cache(allow_output_mutation=True)
def transcribe(audio_file_path, api_key):
    """Transcribe the specified audio file using OpenAI's Whisper model."""
    try:
        openai.api_key = api_key
        with open(audio_file_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
            return transcription['text'] if 'text' in transcription else "No transcript available."
    except Exception as e:
        st.error(f"Failed to transcribe audio: {str(e)}")
        return ""

@st.cache(allow_output_mutation=True)
def summarize_transcription(transcription, context, api_key):
    """Summarize the transcription using OpenAI's language model with additional context."""
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": f"Please summarize this transcription, create action points, decisions: {context}"},
        {"role": "user", "content": transcription}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response['choices'][0]['message']['content'] if response else "Summarization failed."

def generate_epics_and_tasks(summary, context=""):
    """Generate structured breakdown into epics and tasks, including dependencies and story points."""
    messages = [
        {"role": "system", "content": "Generate a structured breakdown of epics and tasks from the summary. Include possible dependencies and estimated effort in story points."},
        {"role": "user", "content": summary}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response['choices'][0]['message']['content'].strip().split('\n') if response else ["Breakdown generation failed."]

def visualize_epics_tasks_dependencies(breakdown_items):
    """Visualize epics, tasks, and dependencies using a graph."""
    fig = go.Figure()

    for item in breakdown_items:
        if item:
            epic, tasks = item.split(':')
            tasks = tasks.split(',')
            for task in tasks:
                fig.add_trace(go.Scatter(x=[epic, task], y=[0, 1], mode='lines+markers', name=task))
    
    fig.update_layout(title='Epics, Tasks, and Dependencies Visualization',
                      xaxis_title='Items',
                      yaxis_title='Progress',
                      showlegend=False)

    return fig

def main():
    st.set_page_config(layout="wide")
    st.title("From Audio to JIRA and Confluence")
    st.subheader("Audio and Video Upload and Transcription App")
    temp_dir = r'C:\Temp\transcripts'
    ensure_directory_exists(temp_dir)
    api_key = st.text_input("Enter your OpenAI API key:", type="password")  # Collect API key securely

    # Define column widths
    cols = st.columns(3)  # Adjust the number of columns if necessary

    # Column 1: Upload and Transcribe
    with cols[0]:
        with st.expander("Transcribe Audio/Video"):
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
                    st.session_state.transcription = transcription  # Store transcription in session state

    # Column 2: Summarize Transcript
    with cols[1]:
        if 'transcription' in st.session_state:
            with st.expander("Summarize Transcript"):
                summarization_context = st.text_input("Enter context for better summarization:")
                if st.button("Summarize"):
                    summary = summarize_transcription(st.session_state.transcription, summarization_context, api_key)
                    st.text_area("Summary:", value=summary, height=200)
                    st.session_state.summary = summary  # Store summary in session state

    # Column 3: Breakdown into Epics and Tasks
    with cols[2]:  # Correct the index from cols[3] to cols[2]
        if 'summary' in st.session_state:
            with st.expander("Breakdown into Epics and Tasks"):
                context = st.text_input("Enter context to enhance the breakdown:")
                if st.button("Generate Breakdown"):
                    breakdown_items = generate_epics_and_tasks(st.session_state.summary, context)
                    st.write("Generated Breakdown:")
                    for item in breakdown_items:
                        if item:
                            st.write(item)

   
    # Visualize epics, tasks, and dependencies outside of columns
    if 'summary' in st.session_state:
        breakdown_items = generate_epics_and_tasks(st.session_state.summary, context)
        fig = visualize_epics_tasks_dependencies(breakdown_items)
        st.write(fig)

    # Cleanup
    if uploaded_file is not None:
        os.remove(file_name)
        if file_type == "mp4":
            os.remove(audio_file_path)

if __name__ == "__main__":
    main()
