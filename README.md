Scrum Team Assistant
This application helps scrum teams streamline requirement capture, transcription, summarization, and visualization for better project management. It uses OpenAI's Whisper model for transcription and GPT-4 for summarization and task breakdown. The application includes several visualization tools to depict task dependencies.



Features
Transcribe Audio/Video: Upload audio or video files to extract and transcribe spoken content.
Summarize Transcription: Transform detailed transcriptions into concise summaries suitable for scrum meetings.
Generate Epics and Tasks: Create structured epics and tasks from summaries, ready for import into Jira.
Update Confluence Page: Automatically update Confluence pages with summarized content.
Visualize Dependencies: View task dependencies through various visualizations including network graphs, sunburst charts, treemaps, and dependency matrices.
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/scrum-team-assistant.git
cd scrum-team-assistant
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Run the application:

bash
Copy code
streamlit run app.py
Usage
Transcribe Audio/Video
Upload an audio or video file.
The application will extract audio from video files if necessary.
Click "Start Transcription" to transcribe the audio.
Summarize Transcript
Provide context for better summarization.
Click "Summarize" to get a concise summary of the transcription.
Generate Epics and Tasks
Provide context to enhance the breakdown.
Click "Generate Breakdown" to create structured epics and tasks.
Update Confluence Page
Enter your Confluence URL, email, and API token.
Provide the space key, page ID, and page title.
Click "Update Page on Confluence" to update the page with the summary.
Visualize Dependencies
The application generates a breakdown of epics and tasks.
View task dependencies through different visualizations like network graphs, sunburst charts, treemaps, and dependency matrices.
Screenshots
Transcription and Summarization

Epics and Tasks Breakdown

Visualizations
