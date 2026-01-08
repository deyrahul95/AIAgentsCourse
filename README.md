# Agentic AI Course | Udemy

## Ambiguity on what Agents actually are:

<strong> "AI agents are programs where LLM outputs control the workflow" </strong>

In practise, describes an AI solution that involves any or all of these:

    1. Multiple LLM calls
    2. LLMs with ability to use Tools
    3. An environment where LLM interact
    4. A Planner to coordinate activities
    5. Autonomy

## Agentic Systems

Anthropic distinguishes two types:

    1. Workflows are systems where LLMs and tools are orchestrated through predefined code paths

    2. Agents are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks


## 5 Workflow Design Patterns

#### 1. PROMPT CHAINING

Decompose into fixed sub-tasks

```
IN -> LLM1 -> Gate -> LLM2 -> LLM3 -> OUT
```

### 2. ROUTING

Direct an input into a specialized sub-task, ensuring separation in concerns

```
                LLM1
                /
IN -> LLM Router -> LLM2 -> OUT 
                \
                LLM3
```

### 3. PARALLELIZATION

Breaking down tasks and running multiple subtask concurrently

```
                     LLM1
                  /       \
IN -> Coordinator -> LLM2 -> Aggregator -> OUT
       (Code)     \       /   (Code)
                     LLM3
```

### 4. ORCHESTRATOR-WORKER

Complex tasks are broken down dynamically and combined

```
                     LLM1
                  /       \
IN -> Orchestrator -> LLM2 -> Synthesizer -> OUT
       (Model)    \       /    (Model)
                     LLM3
```

### 5. EVALUATOR-OPTIMIZER

LLM output is validated by another LLM

```
                   Solution             Accepted
IN ---->   LLM     -------->      LLM    ------>  OUT
        Generator  <--------   Evaluator
                   Rejected
                With Feedback
```

