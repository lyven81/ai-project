from data import get_options


def run_round(agent, campaigns, round_num):
    options = get_options(campaigns, agent.channel, n=3)
    chosen, budget_pct, reasoning = agent.decide(options, round_num)
    allocated = agent.budget * budget_pct
    record = agent.apply_result(chosen, allocated, round_num, reasoning)
    record["options"] = options
    return record
