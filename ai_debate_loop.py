import os
from openai import OpenAI

client = OpenAI()

def run_ai_debate(problem_statement: str, max_rounds: int = 2):
    print(f"\n[Problem Statement]: {problem_statement}\n" + "="*50)
    agent_a_system = "You are Agent Alpha: An analytical, cautious, and highly structural strategist."
    agent_b_system = "You are Agent Beta: An innovative, fast-moving, and pragmatic builder."

    history_a, history_b = [], []
    current_proposal = problem_statement

    for round_num in range(1, max_rounds + 1):
        print(f"--- Round {round_num} ---")
        prompt_a = f"Current plan/problem:\n{current_proposal}\n\nProvide critique or improvements."
        res_a = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": agent_a_system}] + history_a + [{"role": "user", "content": prompt_a}])
        proposal_a = res_a.choices[0].message.content
        print(f"\n[Agent Alpha]:\n{proposal_a}\n")
        
        history_a.append({"role": "user", "content": prompt_a})
        history_a.append({"role": "assistant", "content": proposal_a})

        prompt_b = f"Review Alpha's output:\n{proposal_a}\n\nProvide a polished, actionable version."
        res_b = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": agent_b_system}] + history_b + [{"role": "user", "content": prompt_b}])
        proposal_b = res_b.choices[0].message.content
        print(f"\n[Agent Beta]:\n{proposal_b}\n")
        
        history_b.append({"role": "user", "content": prompt_b})
        history_b.append({"role": "assistant", "content": proposal_b})
        current_proposal = proposal_b

    print("="*50 + "\n[Final Consensus]:\n" + current_proposal)
    return current_proposal

if __name__ == "__main__":
    run_ai_debate("How can we streamline multi-agent file syncing via GitHub?", max_rounds=1)
