import os
import streamlit as st
import openai
from moviepy.editor import VideoFileClip
import pandas as pd
import streamlit.components.v1 as components
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from atlassian import Confluence



# Function to ensure the specified directory exists
def ensure_directory_exists(directory):
    """Ensure that the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

@st.cache
def extract_audio(video_file_path, output_audio_path):
    """Extract audio from a video file and save it as an MP3 file."""
    video = VideoFileClip(video_file_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path, codec='mp3')
    audio.close()
    video.close()

@st.cache
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

@st.cache
def summarize_transcription(transcription, context, api_key):
    """Summarize the transcription using OpenAI's language model with additional context to include dependencies."""
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": f"Summarize this detailed transcript into a concise format suitable for Scrum: identify key user stories, tasks, acceptance criteria, and their dependencies that align with the project goals: {context}"},
        {"role": "user", "content": transcription}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response['choices'][0]['message']['content'] if response else "Summarization failed."

def generate_epics_and_tasks(summary, context=""):
    """Generate a structured breakdown into epics, tasks, and their dependencies with clear parent-child relationships and estimated story points, formatted for CSV output."""
    prompt_text = f"""
    Based on the provided summary, create a structured breakdown of the software project into epics, tasks, and their dependencies suitable for a Jira import. 
    For each task, specify the task summary, issue type (like Task or Epic), the epic it belongs to (if any), estimated story points, and any dependencies.

    Summary: {summary}
    Context (Project Goals): {context}

    Example Output:
    Summary: Design login page, Issue Type: Task, Epic Name: User Authentication System, Story Points: 3, Dependencies: User Authentication System
    Summary: Implement OAuth integration, Issue Type: Task, Epic Name: User Authentication System, Story Points: 8, Dependencies: Design login page
    Summary: User Authentication System, Issue Type: Epic, Epic Name: , Story Points: 
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt_text}],
        temperature=0.3  # Lower temperature for more deterministic output
    )

    if response:
        breakdown_text = response['choices'][0]['message']['content'].strip()
        return parse_breakdown_from_text(breakdown_text)
    return ["Breakdown generation failed."]

def parse_breakdown_from_text(breakdown_text):
    """Parse the structured text breakdown into a list of dictionaries formatted for CSV output, including dependencies."""
    lines = breakdown_text.split('\n')
    structured_breakdown = []

    for line in lines:
        parts = line.split(", ")
        if len(parts) >= 5:  # Ensure there are at least five parts to capture dependencies
            summary = parts[0].split(": ")[1] if len(parts[0].split(": ")) > 1 else ""
            issue_type = parts[1].split(": ")[1] if len(parts[1].split(": ")) > 1 else ""
            epic_name = parts[2].split(": ")[1] if len(parts[2].split(": ")) > 1 else ""
            story_points = parts[3].split(": ")[1] if len(parts[3].split(": ")) > 1 else ""
            dependencies = parts[4].split(": ")[1] if len(parts[4].split(": ")) > 1 else ""
            structured_breakdown.append({
                'Summary': summary,
                'Issue Type': issue_type,
                'Epic Name': epic_name,
                'Story Points': story_points,
                'Dependencies': dependencies
            })
        else:
            print(f"Skipping line due to incorrect format: {line}")

    return structured_breakdown

def export_to_csv(breakdown_items, filename="output.csv"):
    df = pd.DataFrame(breakdown_items)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename} successfully.")

def define_layout():
    return {
        'title': 'Network Graph Visualization',
        'titlefont_size': 16,
        'showlegend': False,
        'hovermode': 'closest',
        'margin': {'b': 20, 'l': 5, 'r': 5, 't': 40},
        'annotations': [{
            'text': "Network graph showing dependencies among epics and tasks",
            'showarrow': False,
            'xref': "paper",
            'yref': "paper",
            'x': 0.005,
            'y': -0.002
        }],
        'xaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False},
        'yaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False}
    }

def format_breakdown(breakdown):
    """Format breakdown into a structured list for visualization."""
    formatted = []
    current_epic = None
    for line in breakdown:
        if "Epic" in line:
            current_epic = line.strip()
        elif "Task" in line and current_epic:
            formatted.append({'task': line.strip(), 'epic': current_epic})
    return formatted

def visualize_dependencies_with_pyvis():
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.add_node(1, label="Node 1")
    net.add_node(2, label="Node 2")
    net.add_edge(1, 2)
    net.show("temp.html")
    HtmlFile = open("temp.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=800)

def visualize_dependencies_with_networkx(breakdown_items):
    G = nx.DiGraph()
    for item in breakdown_items:
        if item:  # Ensure that each item is valid
            epic = item.get('Epic Name')
            task = item.get('Summary')
            G.add_node(epic, label=epic, color='lightblue')  # Add epic as node
            G.add_node(task, label=task, color='orange')  # Add task as node
            G.add_edge(epic, task)  # Add an edge from epic to task

    pos = nx.spring_layout(G)  # Position nodes for better visibility
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold', width=2, edge_color='k')
    st.pyplot(plt)  # Display the figure in Streamlit
    plt.close()

def visualize_dependencies_with_plotly(breakdown_items):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    for item in breakdown_items:
        epic = item['Epic Name']
        task = item['Summary']
        G.add_node(epic, label=epic, group='Epic')
        G.add_node(task, label=task, group='Task')
        G.add_edge(epic, task)

    # Generate positions and edges for Plotly
    pos = nx.spring_layout(G)
    edge_trace, node_trace = create_plotly_traces(G, pos)

    # Define figure layout using the define_layout function
    fig = go.Figure(data=[edge_trace, node_trace], layout=define_layout())
    st.plotly_chart(fig, use_container_width=True)

def visualize_sunburst(formatted_breakdown):
    labels = [item['epic'] for item in formatted_breakdown] + [item['task'] for item in formatted_breakdown]
    parents = [""] + [item['epic'] for item in formatted_breakdown]
    values = [1] * len(labels)  # Assigning a default value of 1 for simplicity

    fig = px.sunburst(
        names=labels,
        parents=parents,
        values=values,
        title="Sunburst Chart of Epics and Tasks",
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)

def visualize_treemap(formatted_breakdown):
    labels = [item['epic'] for item in formatted_breakdown] + [item['task'] for item in formatted_breakdown]
    parents = [""] + [item['epic'] for item in formatted_breakdown]
    values = [1] * len(labels)  # Assigning a default value of 1 for simplicity

    fig = px.treemap(
        names=labels,
        parents=parents,
        values=values,
        title="Treemap of Epics and Tasks",
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)

def process_to_dataframe(breakdown_items):
    """
    Converts a list of breakdown items into a pandas DataFrame, including a column for dependencies.
    """
    data = []
    for item in breakdown_items:
        # Ensure all keys are present and fallback to default values if not
        summary = item.get('Summary', '')
        issue_type = item.get('Issue Type', '')
        epic_name = item.get('Epic Name', '')
        story_points = item.get('Story Points', '')
        dependencies = item.get('Dependencies', '')  # Ensuring dependencies are handled

        data.append({
            'Summary': summary,
            'Issue Type': issue_type,
            'Epic Name': epic_name,
            'Story Points': story_points,
            'Dependencies': dependencies  # Adding dependencies to data
        })

    df = pd.DataFrame(data, columns=['Summary', 'Issue Type', 'Epic Name', 'Story Points', 'Dependencies'])  # Include dependencies in DataFrame columns
    return df

def create_plotly_traces(G, pos):
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            color=[],
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right')
        ))

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([f'{node}'])

    # Add color to node points by the number of connections
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
    
    return edge_trace, node_trace

def generate_dependency_matrix(breakdown_items):
    """Generate a dependency matrix from the breakdown items."""
    tasks = [item['Summary'] for item in breakdown_items]
    matrix = pd.DataFrame(0, index=tasks, columns=tasks)

    for item in breakdown_items:
        task = item['Summary']
        dependencies = item['Dependencies'].split('; ')
        for dependency in dependencies:
            if dependency in tasks:
                matrix.at[task, dependency] = 1

    return matrix

def plot_dependency_heatmap(matrix):
    """Plot a heatmap from the dependency matrix with adjusted size."""
    fig = px.imshow(matrix,
                    labels=dict(x="Depends On", y="Tasks", color="Dependency"),
                    x=matrix.columns,
                    y=matrix.index,
                    text_auto=True,
                    title="Dependency Matrix",
                    aspect='auto')  # 'auto' adjusts the aspect ratio to fill the container

    # Adjust layout to increase size
    fig.update_layout(
        width=800,  # Set the width of the figure
        height=600,  # Set the height of the figure
        autosize=True  # Allow the layout size to adjust based on the container
    )
    st.plotly_chart(fig, use_container_width=True)



def update_confluence_page(confluence, space, title, content, page_id):
    """Update an existing Confluence page with the specified content."""
    status = confluence.update_page(
        page_id=page_id,
        title=title,
        body=content
    )
    return status



def main():
    st.set_page_config(layout="wide")
    st.title("Scrum Team Assistant")
    st.subheader("Streamlining Requirement Capture for Scrum Teams")
    temp_dir = r'C:\Temp\transcripts'
    ensure_directory_exists(temp_dir)
    api_key = st.text_input("Enter your OpenAI API key:", type="password")

    # Define column widths
    cols = st.columns(3)

    # Column 1: Upload and Transcribe
    with cols[0]:
        with st.expander("Transcribe Audio/Video"):
            st.write("Upload audio or video files capturing discussions about requirements or functionalities. This tool will extract and transcribe the spoken content, preparing it for further analysis and summarization.")
            uploaded_file = st.file_uploader("Choose a file", type=["mp3", "mp4", "m4a"])
            if uploaded_file is not None:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                file_type = uploaded_file.type.split('/')[1]
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                if file_type == "mp4":
                    audio_path = file_path.split('.')[0] + '.mp3'
                    extract_audio(file_path, audio_path)
                    st.video(file_path)
                else:
                    audio_path = file_path
                    st.audio(file_path, format=f'audio/{file_type}')
                if st.button("Start Transcription"):
                    transcription = transcribe(audio_path, api_key)
                    st.text_area("Transcription:", value=transcription, height=200)
                    st.session_state.transcription = transcription

    # Column 2: Summarize Transcript
    with cols[1]:
        if 'transcription' in st.session_state:
            with st.expander("Summarize Transcript"):
                st.write("Utilize this feature to transform detailed transcriptions into concise summaries. These summaries highlight key points and are tailored for easy assimilation by your scrum team, streamlining your project management process.")
                summarization_context = st.text_input("Enter context for better summarization:")
                if st.button("Summarize"):
                    summary = summarize_transcription(st.session_state.transcription, summarization_context, api_key)
                    st.text_area("Summary:", value=summary, height=200)
                    st.session_state.summary = summary


        if 'summary' in st.session_state:
            with st.expander("Update Confluence Page"):
                confluence_url = st.text_input("Confluence URL", value="https://your-confluence.atlassian.net/wiki")
                email = st.text_input("Email")
                api_token = st.text_input("API Token", type="password")
                confluence = Confluence(url=confluence_url, username=email, password=api_token)

                space_key = "~6278d6d083954200696720b3"
                page_id = "54722580"
                page_title = "streamlit"

                if st.button("Update Page on Confluence"):
                    status = update_confluence_page(confluence, space_key, page_title, st.session_state.summary, page_id)
                    if 'id' in status:
                        st.success("Confluence page updated successfully!")
                    else:
                        st.error("Failed to update Confluence page")




    # Column 3: Breakdown into Epics and Tasks
    with cols[2]:
        if 'summary' in st.session_state:
            with st.expander("Breakdown into Epics and Tasks"):
                st.write("Convert summaries into structured epics and tasks directly importable into Jira. This section facilitates the organization of project deliverables, ensuring clear and effective task management and alignment with overall project objectives.")
                context = st.text_input("Enter context to enhance the breakdown:")
                if st.button("Generate Breakdown"):
                    breakdown_items = generate_epics_and_tasks(st.session_state.summary, context)
                    st.session_state.breakdown_items = breakdown_items
                    st.write("Generated Breakdown:")
                    for item in breakdown_items:
                        st.write(item)



    #st.divider()


    # Visualization and Dataframe under expander
    if 'breakdown_items' in st.session_state and st.session_state.breakdown_items:
        if not isinstance(st.session_state.breakdown_items, str):
            with st.expander("Dependency Matrix"):
                
                # DataFrame display
                df_breakdown = process_to_dataframe(st.session_state.breakdown_items)
                dependency_matrix = generate_dependency_matrix(st.session_state.breakdown_items)

                st.dataframe(df_breakdown)
                plot_dependency_heatmap(dependency_matrix)

        else:
            st.error("Failed to generate a valid breakdown.")

        #st.divider()

if __name__ == "__main__":
    main()
