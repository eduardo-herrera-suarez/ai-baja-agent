from langfuse import Langfuse
from backend.nodes.confidence_node import confidence_node

langfuse = Langfuse()

def run_agent(user_input: str):
    try:
        # Create a trace (correct method name may differ → use create_trace)
        trace = langfuse.create_trace(
            name="ai_baja_agent",
            input={"user_input": user_input}
        )

        result = confidence_node(user_input)

        # Log output
        langfuse.create_observation(
            name="agent_execution",
            input={"user_input": user_input},
            output=result,
            trace_id=trace.id
        )

        return result

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    output = run_agent("Plan a trip to Baja California")
    print(output)