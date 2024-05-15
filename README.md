[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://scrum-team-assistant.streamlit.app/)

# Scrum Team Assistant

This application helps scrum teams streamline requirement capture, transcription, summarization, and visualization for better project management. It uses OpenAI's Whisper model for transcription and GPT-4 for summarization and task breakdown. The application includes several visualization tools to depict task dependencies.

## Features

- **Transcribe Audio/Video**: Upload audio or video files to extract and transcribe spoken content.
- **Summarize Transcription**: Transform detailed transcriptions into concise summaries suitable for scrum meetings.
- **Generate Epics and Tasks**: Create structured epics and tasks from summaries, ready for import into Jira.
- **Update Confluence Page**: Automatically update Confluence pages with summarized content.
- **Visualize Dependencies**: View task dependencies through various visualizations including network graphs, sunburst charts, treemaps, and dependency matrices


## Technologies and Libraries Used

- **Python**: The core programming language used for this application.
- **Streamlit**: Used for building the web application interface.
- **OpenAI**: Utilized for transcription and summarization with Whisper and GPT-4 models.
- **MoviePy**: Used for video and audio processing.
- **Pandas**: Data manipulation and analysis.
- **Plotly**: Interactive library for visualization.
- **Atlassian Python API**: Used for interacting with Confluence.
- 
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/scrum-team-assistant.git
    cd scrum-team-assistant
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    streamlit run app.py
    ```

## Usage

### Transcribe Audio/Video

1. Upload an audio or video file.
2. The application will extract audio from video files if necessary.
3. Click "Start Transcription" to transcribe the audio.

![Transcribe Audio/Video](https://github.com/tsitsidalakishvili/Scrum_Assistant/blob/main/screenshots/1.png)

### Summarize Transcript

Click "Summarize" to transform detailed transcriptions into concise summaries suitable for scrum meetings

![Summarize Transcription](https://github.com/tsitsidalakishvili/Scrum_Assistant/blob/main/screenshots/2.png)

### Generate Epics and Tasks

Click "Generate Breakdown" to create structured epics and tasks.

![Generate Epics and Tasks](https://github.com/tsitsidalakishvili/Scrum_Assistant/blob/main/screenshots/3.png)

### Update Confluence Page

1. Enter your Confluence URL, email, and API token.
2. Provide the space key, page ID, and page title.
3. Click "Update Page on Confluence" to update the page with the summary.

### Visualize Dependencies

View task dependencies through dependency matrices.

![Visualize Dependencies](https://github.com/tsitsidalakishvili/Scrum_Assistant/blob/main/screenshots/4.png)
