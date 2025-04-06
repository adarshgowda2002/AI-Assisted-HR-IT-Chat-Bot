def log_message(role, content, filename="chat_history.txt"):
    with open(filename, "a") as file:
        file.write(f"{role}: {content}\n")


