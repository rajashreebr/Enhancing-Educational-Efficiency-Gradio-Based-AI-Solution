import gradio as gr
import requests
from openai import OpenAI
import mermaid as md
from mermaid.graph import Graph


intro_text = """
Unlock knowledge at your fingertips with our AI-powered personal tutor. 
Whether tackling tough topics or curious questions, our Large Language Model offers clear, concise guidance anytime. 
Dive into learning with tailored explanations and expert insights. Ready to explore? Ask away!"""



content_system_prompt = """ You are Educational Expert. Generate course content in this fomat.
  - *Title*: Guidelines for Structured Responses
  - **Headings and Subheadings**: Use headings and subheadings to break down the topic into manageable sections. This helps in guiding the reader through the content logically.
  - *Title*: Clearly state the topic of discussion.
  - *Description*: Provide a brief overview of the topic, explaining its relevance or importance.
  - *Detailed Explanations*: Under relevant headings and subheadings, delve into the specifics of the topic. Use bullet points to list features, steps, or important notes.
  - *Conclusion*: Summarize the main points discussed and provide a closing thought or recommendation.
  - **Bullet Points**: Employ bullet points to list information that does not require a sequential order. This can include examples, features, benefits, or any other information that enhances understanding of the topic.
   Conclusion: Conclusion of the topic
"""
quiz_system_prompt ="""You are Educational Expert generated accurate quiz questions to validate student understanding.
For the given content, generate quiz questions one in each line with four options to answer. 
"""

graph_system_prompt ="""You are Graph Language expert.
For the given content, generate the graph representation in mermaid syntax. Only return the graph text don't include extra content.
"""

# Function to get answer from localhost and speak it out
def generate_with_llm(query,system_prompt):
    # Replace 'localhost_url' with your actual localhost URL
    client = OpenAI(api_key="Your openAI API key")

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
    temperature=0.7,max_tokens=2048
    )
    answer = completion.choices[0].message.content
    return answer

def generate_content(query):
    if query == "":
        return "Please enter a valid question or topic."
    # get course material
    content_text = generate_with_llm(query,content_system_prompt)
    return content_text

def generate_quiz(content):
    if content == "":
        return "Please enter a valid question or topic to generate content then Try."
    # get quiz questions
    quiz_text = generate_with_llm(content,quiz_system_prompt)
    return quiz_text

def generate_graph(content):
    try:
        graph_text = generate_with_llm(content, graph_system_prompt)
        graph = Graph('example-flowchart', graph_text)
        graphe = md.Mermaid(graph)
        graphe.to_svg("graph.svg")
        return "graph.svg"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def create_content_pdf(content):
    print("PDF content",content)
    from markdown_pdf import MarkdownPdf, Section

    pdf = MarkdownPdf()
    pdf.meta["title"] = "User Guide"
    pdf.add_section(Section(content, toc=False))
    pdf.save("content.pdf")

def create_quiz_pdf(quiz):
    from markdown_pdf import MarkdownPdf, Section

    pdf = MarkdownPdf()
    pdf.meta["title"] = "User Guide"
    pdf.add_section(Section(quiz, toc=False))
    pdf.save("quizz.pdf")

def create_graph_pdf(graph):
    return "graph.svg"

# # Define the Gradio interface with updated requirements
# iface = gr.Interface(
#     fn=lambda x: (generate_with_llm(x,content_system_prompt), generate_with_llm(x,quiz_system_prompt), generate_with_llm(x,graph_system_prompt)), 
#     inputs=gr.Textbox(lines=7, label="Enter your question or topic here"), 
#     outputs=[gr.Textbox(label="Course Material"),
#              gr.Textbox(label="Quizz"),
#              gr.Image(label="Graph Representation")],
#     title="Personal Tutor",
#     description="AI Assitant to generate Educational content for your review.",
#     allow_flagging=False
# )

# # Launch the app
# iface.launch()

# Gradio Blocks

with gr.Blocks() as demo:
    heading = gr.Markdown(f"""# Personal Tutor
                      """)
    
    gr.Markdown("""## Ask a question or topic to generate course material, quiz questions and graph representation.""")
    query = gr.Textbox(lines=7, label="Enter your question or topic here")
    
    # create a horizontal line
    gr.Markdown("---")
    
    gr.Markdown("""## Generate Course Material.
                
                AI Assitant to generate Educational content for your review.""")
   

    content = gr.Textbox(label="Course Material")
    with gr.Row():
            gr.Button("Generate Course Material").click(
            fn=generate_content,
            inputs=query,
            outputs=content
            )
            gr.DownloadButton("Download as PDF",value="content.pdf").click(
            fn=create_content_pdf,
            inputs=content,
            outputs=None
            )
    
    gr.Markdown("""## Generate Quiz. 
                Once you have the course material, generate quiz questions to validate student understanding.""")
    
    quiz = gr.Textbox(label="Quizz")
    with gr.Row():
        gr.Button("Generate Quiz").click(
            fn=generate_quiz,
            inputs=content,
            outputs=quiz
        )
        gr.DownloadButton("Download Quiz",value="quizz.pdf").click(
            fn=create_quiz_pdf,
            inputs=quiz,
            outputs=None
        )
        
    
    
    gr.Markdown("""## Generate Graph. 
                Graphical representation of the content.""")
    graph = gr.Image(label="Graph Representation")
    with gr.Row():
        gr.Button("Generate Graph").click(
            fn=generate_graph,
            inputs=content,
            outputs=graph
        )
        gr.DownloadButton("Download Graph", value="graph.svg").click(
            fn=create_graph_pdf,
            inputs=content,
            outputs=None
        )
    

demo.launch(allowed_paths=["/content","/quizz","/graph"])

