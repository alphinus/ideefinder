"""
Parallel Agent Executor
Runs multiple agents concurrently for Phase 2
"""
import asyncio
from typing import List, Callable, Any, Dict
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


async def run_agents_parallel(
    agents: List[tuple[str, Callable]],
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Run multiple agents in parallel

    Args:
        agents: List of (agent_name, async_function) tuples
        show_progress: Show rich progress bar

    Returns:
        Dict mapping agent_name to result
    """
    results = {}

    if show_progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            # Create tasks
            tasks = []
            progress_tasks = {}

            for agent_name, agent_func in agents:
                task_id = progress.add_task(f"[cyan]{agent_name}...", total=100)
                progress_tasks[agent_name] = task_id
                tasks.append(agent_func())

            # Run all agents concurrently
            agent_results = await asyncio.gather(*tasks)

            # Mark all complete
            for agent_name in progress_tasks:
                progress.update(progress_tasks[agent_name], completed=100)

            # Map results
            for (agent_name, _), result in zip(agents, agent_results):
                results[agent_name] = result
    else:
        # Run without progress bar
        tasks = [agent_func() for _, agent_func in agents]
        agent_results = await asyncio.gather(*tasks)

        for (agent_name, _), result in zip(agents, agent_results):
            results[agent_name] = result

    return results
