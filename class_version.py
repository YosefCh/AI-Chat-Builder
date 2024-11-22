# enter you file path to the file that contains your Api key or you can use an environment variable
with open('C:/Users/Rebecca/OneDrive/Documents/Python AI/LLM (AI) Browser History Analyzer/Api_key.txt', 'r') as f:
    # set a constant variable to the key
    API_KEY = f.readline().strip()

class OpenAIClient:
    """
    A client for interacting with the OpenAI API.

    Attributes:
        api_key (str): The API key for authenticating with the OpenAI API.
        model_name (str): The name of the model to use for generating responses.
        max_tokens (int): The maximum number of tokens to generate in the response.
        system_role_content (str): The content for the system role in the conversation.
        temperature (float): The randomness of the model's responses.
        top_p (float): The cumulative probability threshold for top-p sampling.

    Methods:
        get_response(prompt: str) -> str:
            Generates a response from the OpenAI API based on the given prompt.
    """
 
    def __init__(self, api_key=API_KEY, 
                 model_name="gpt-4o-mini", 
                 max_tokens=4096, 
                 system_role_content="You are a helpful assistant.", 
                 temperature=.3, 
                 top_p=.6):
        """
        Initializes the OpenAIClient with the given parameters.

        Args:
            api_key (str): The API key for authenticating with the OpenAI API.
            model_name (str): The name of the model to use for generating responses. Defaults to "gpt-4o-mini".
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 4096.
            system_role_content (str): The content for the system role in the conversation. Defaults to "You are a helpful assistant.".
            temperature (float): The randomness of the model's responses. We chose a default of 0.3
            top_p (float): The cumulative probability threshold for top-p sampling. We chosse a default of 0.6
        """
        import openai
        openai.api_key = api_key
        self.client = openai
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.system_role_content = system_role_content
        self.temperature = temperature
        self.top_p = top_p

    def get_response(self, prompt):
        """
        Generates a response from the OpenAI API based on the given prompt.

        Args:
            prompt (str): The prompt to send to the OpenAI API.

        Returns:
            str: The response generated by the OpenAI API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_role_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(e)


# sample code to to run in the terminal
if __name__ == "__main__":
    a = OpenAIClient(model_name="gpt-4o",temperature=.5, top_p=1.0)
    print(a.get_response("Who is Eliezer Yudkowsky?"))