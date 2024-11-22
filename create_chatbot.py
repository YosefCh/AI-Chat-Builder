from IPython.display import display, Markdown, HTML
import markdown2
import logging
import random

# Suppress INFO messages from httpx as there can be distracting messages that aren't relevant to the user
logging.getLogger("httpx").setLevel(logging.ERROR)

class Chatbot:
    def __init__(self, model_name, system_role_content, max_inputs, input_length_limit, tone):
        # set instance variables
        self.max_inputs = max_inputs
        self.input_length_limit = input_length_limit
        # Initialize history list to store the conversation history
        self.history = []
        # Initialize input count to keep track of the number of inputs
        self.input_count = 0

        # Set tone parameters by calling set_tone method defined below
        self.set_tone(tone)
        
        from class_version import OpenAIClient
        # Initialize the AI instance with the tone parameters
        self.ai = OpenAIClient(
            model_name=model_name,
            system_role_content=system_role_content,
            
            # use the values set by set_tone method 
            temperature=self.temperature,
            top_p=self.top_p
        )

    def set_tone(self, tone):
        # set temperature and top_p based on the tone by choosing random value within the given range
        if tone == "creative":
            self.temperature = random.uniform(0.8, 1.35)
            self.top_p = random.uniform(0.8, 1.0)
        elif tone == "balanced":
            # there is a buffer zone of .7 to .8 to create a defined difference between balanced and creative
            self.temperature = random.uniform(0.4, 0.7)
            self.top_p = random.uniform(0.4, 0.7)
        elif tone == "precise":
            # there is a buffer zone of .3 to .4 to create a defined difference between balanced and precise
            self.temperature = random.uniform(0.0, 0.3)
            self.top_p = random.uniform(0.0, 0.3)
        else:
            raise ValueError("Invalid tone. Choose from 'creative', 'balanced', or 'precise'.")

    def chat(self):
        # loop to continue the conversation until the max_inputs is reached or the user types "exit" or "quit"
        while self.input_count < self.max_inputs:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            if len(user_input.split()) > self.input_length_limit:
                display(Markdown(f"__Error: Input exceeds the length limit of {self.input_length_limit} words.__"))
                # skip the current iteration and continue with the next iteration
                continue

            # Display user prompt
            display(HTML(f'''
                        <article style="background-color: rgb(70, 70, 70); margin: 10px; padding: 10px; height: auto; 
                        line-height: 1.5; width: 75%"><b>You:</b> {user_input}</article>
                        '''))

            # Add user input to history
            self.history.append(f"User: {user_input}")

            # Create a prompt with the conversation history by using the join method to concatenate the list of prompts and responses
            prompt = "\n".join(self.history) + f"\nAI:"

            # Get the AI response
            response = self.ai.get_response(prompt)

            # Add AI response to history
            self.history.append(f"AI: {response}")

            # Increment the input count
            self.input_count += 1
            
            # Convert the AI response to HTML format while trying to retain the markdown formatting. (It isn't perfect. The bolding seems to have gotten lost.)
            response_to_html = markdown2.markdown(response)
            
            display(HTML(f'''
                        <main style="background-color: rgb(0, 255, 0); margin: 10px; padding: 10px; height: auto; 
                        line-height: 1.5; width: 75%"><b>AI:</b> {response_to_html}</main>
                        '''))
            
        if self.input_count >= self.max_inputs:
            display(Markdown(f"### __This conversation has reached the limit of {self.max_inputs} inputs.__"))
        self.save_conversation()

    def save_conversation(self):
        from class_version import OpenAIClient
        self.ai = OpenAIClient(
            model_name='gpt-4o-mini',
            system_role_content="You are a helpful assistant.",
            temperature=0.1,
            top_p=0.1
        )
        name = self.ai.get_response(f"""The following is a record of a conversation between a user and an AI assistant: {self.history}
                            Please find a word or a phrase with which to name this conversation to be the name of the file.
                            The name should be no longer than three words and should not contain any special characters or spaces.""")

        # Define the directory path
        import os
        directory = "C:/Users/Rebecca/OneDrive/Documents/Python AI/AI Conversations"

        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Use the directory path when opening the file
        file_path = os.path.join(directory, name)

        with open(file_path + ".html", "w") as file:
            
            import datetime
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html_template =(f"""<!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                        body {{
                            background-color: rgb(180, 222, 229);  /* Teal-gray background */
                            margin: 40px;
                            padding: 20px;
                            font-family: Arial, sans-serif;
                        }}
                        .date {{
                            position: absolute;
                            top: 20px;
                            right: 40px;
                            color: #666;
                        }}
                        .content {{
                            margin-top: 60px;
                        }}
                        .user-message {{
                            margin: 20px 0;  /* Increased margin between messages */
                            padding: 15px;
                            background-color: #f5f5f5;  /* Light gray for user */
                            border-radius: 8px;
                            line-height: 1.6;  /* Increased line height */
                        }}
                        .ai-message {{
                            margin: 20px 0;
                            padding: 15px;
                            background-color: rgb(8, 212, 130);  /* Light teal for AI */
                            border-radius: 8px;
                            line-height: 1.6;
                        }}
                    </style>
                    </head>
                    <body>
                    <div class="date">{date}</div>
                    <h1>{name}</h1>
                    <div class="content">
                    """)
            python_with_html = """
            for i, message in enumerate(self.history):
                css_class = "user-message" if i % 2 == 0 else "ai-message"
                file.write(f'<div class="{css_class}">{message}</div><br><br>\\n')
            file.write("</div></body></html>")
            """
            
            html_dev = OpenAIClient(model_name='gpt-4o-mini', 
                                    system_role_content="You are a skilled web developer.", 
                                    temperature=0.1, 
                                    top_p=0.1)
                
            conversation = html_dev.get_response(f"""Please convert {self.history} to HTML format preserving the markdown formatting it has.
                                     You can use the following code as a template: {html_template} and {python_with_html}.
                                      """)
            
            # Trim the conversation to only include the actual HTML
            start_index = conversation.find("<!DOCTYPE html>")
            end_index = conversation.rfind("</html>") + len("</html>")
            conversation = conversation[start_index:end_index]
            file.write(conversation)  
            
        display(Markdown(f"### __The conversation has been saved as {name}.html.__"))

# Example usage
chatbot = Chatbot(
    model_name="gpt-4o-mini",
    system_role_content="""You are a helpful assistant. """,
    max_inputs=20,
    input_length_limit=1000,
    tone="balanced"
)
chatbot.chat()