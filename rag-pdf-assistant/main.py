from app.generator import generate_response

if __name__ == "__main__":
    # Prompt user for input
    user_query = input("Ask a question: ")
    
    # Hardcoded file path (replace with file upload or CLI args in production)
    file_path = r"C:\Users\CP_LPT-37\Desktop\sample-project\rag-pdf-assistant\app\docs\machine_learning.pdf"

    # Generate and display the response
    response = generate_response(user_query, file_path)
    print("\nResponse:\n", response)
