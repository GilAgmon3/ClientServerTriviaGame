# main.py
import openai

# Replace 'your-openai-api-key' with your actual OpenAI API key
openai.api_key = 'sk-proj-fcuZaq1M1IuerU0NgBCCT3BlbkFJZBD4ELDAioqcWapO2X8D'

TRANSCRIPT_FILE = "transcript.txt"


def get_user_prompt():
    return input("Enter your prompt: ")


def generate_transcript(prompt):
    # Call the OpenAI API to generate text based on the prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()


def save_transcript(transcript):
    with open(TRANSCRIPT_FILE, "a") as file:
        file.write(transcript + "\n\n")


def load_transcripts():
    try:
        with open(TRANSCRIPT_FILE, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def main():
    previous_transcripts = load_transcripts()
    print("Previous Transcripts:")
    print(previous_transcripts)

    while True:
        prompt = get_user_prompt()
        transcript = generate_transcript(prompt)
        print("Generated transcript:")
        print(transcript)

        save_transcript(transcript)

        # Ask if the user wants to continue or exit
        choice = input("Do you want to continue (y/n)? ")
        if choice.lower() != 'y':
            break


if __name__ == "__main__":
    main()
