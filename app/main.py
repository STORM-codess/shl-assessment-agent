from app.services.retrieval import (
    semantic_search
)

from app.services.llm_recommender import (
    recommend_assessments
)

from app.services.session_manager import (

    add_message,

    update_retrieval_results,

    update_llm_response,

    get_session_state,

    clear_session
)


# ---------------------------------------------------
# Main Conversational Agent
# ---------------------------------------------------

def run_agent():

    print(
        "\nSHL Assessment Recommendation Agent"
    )

    print(
        "\nCommands:"
    )

    print(
        "- Type 'exit' to quit"
    )

    print(
        "- Type 'clear' to reset session"
    )

    print()

    while True:

        query = input(
            "\nUser: "
        )

        # -----------------------------------
        # Exit Command
        # -----------------------------------

        if query.lower() == "exit":

            print("\nGoodbye!")

            break

        # -----------------------------------
        # Clear Session Command
        # -----------------------------------

        if query.lower() == "clear":

            clear_session()

            print(
                "\nSession cleared!"
            )

            continue

        try:

            # -----------------------------------
            # Save User Message
            # -----------------------------------

            add_message(
                "user",
                query
            )

            # -----------------------------------
            # Semantic Retrieval
            # -----------------------------------

            retrieved_results = semantic_search(
                query
            )

            # -----------------------------------
            # Update Session Retrieval State
            # -----------------------------------

            update_retrieval_results(
                query,
                retrieved_results
            )

            # -----------------------------------
            # Get Current Session
            # -----------------------------------

            session = get_session_state()

            # -----------------------------------
            # Generate LLM Response
            # -----------------------------------

            response = recommend_assessments(

                query,

                retrieved_results,

                session
            )

            # -----------------------------------
            # Save Assistant Response
            # -----------------------------------

            update_llm_response(
                response
            )

            add_message(
                "assistant",
                response
            )

            # -----------------------------------
            # Final Output
            # -----------------------------------

            print("\nAgent:\n")

            print(response)

        except Exception as e:

            print(
                "\nError occurred:\n"
            )

            print(str(e))


# ---------------------------------------------------
# Run Application
# ---------------------------------------------------

if __name__ == "__main__":

    run_agent()