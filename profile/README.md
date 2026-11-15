<p align="center">
  <img src="https://raw.githubusercontent.com/Valen-Team/.github/main/profile/assets/logo-new.jpg" alt="Valen logo" width="144" />
</p>

<h1 align="center">Valen · 万澜</h1>

<p align="center">
  <strong>Fast Decisions. Continuous Evolution.</strong><br />
  Fast decision models · Recursive self-improvement (RSI) · Agents
</p>

<p align="center">
  <strong>English</strong> · <a href="https://github.com/Valen-Team/.github/blob/main/profile/README_zh-CN.md">简体中文</a>
</p>

<p align="center">
  <a href="https://valen-team.github.io/">Website</a> ·
  <a href="https://huggingface.co/spaces/Valen-Team/Valen-API">Playground</a> ·
  <a href="https://valen-team.github.io/docs/">Documentation</a> ·
  <a href="https://valen-team.github.io/news/">News</a> ·
  <a href="https://huggingface.co/Valen-Team">Hugging Face</a> ·
  <a href="https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard">Leaderboard</a>
</p>

---

**Valen** is an open-source organization bringing together **fast decision models**, **recursive self-improvement (RSI)**, and **agents**. We develop and bring together models, tools, research resources, and applications to help agents make decisions quickly, act in their environments, and improve through experience and feedback.

Our goal is to connect efficient decision-making with agents that can learn and adapt over time. We welcome researchers and developers working across these areas to build, evaluate, and share their work here.

## What We Work On

- **Fast decision models** — low-latency decisions from text, images, and video, with structured outputs that agents can use to select actions, route tasks, and assess states.
- **Recursive self-improvement (RSI)** — methods for learning from experience, reusing memory and skills, improving tools and agent workflows, and updating models. We care about reproducible evidence that these changes lead to better performance over time.
- **Agents** — agent frameworks, tools, and applications that connect perception, planning, decision-making, and execution in interactive environments.

These directions inform one another: decision models help agents choose actions; agent runs produce experience and feedback; RSI methods explore how to turn that feedback into improvements. Evaluation helps establish whether those improvements hold up.

## Open-Source Projects

| Project | What it does | Explore |
| :--- | :--- | :--- |
| **[Valen-Decision](https://github.com/Valen-Team/Valen)** | A multimodal System One decision model: text, images, and video in; structured decision probabilities out. Valen-Decision-1.5 comes in five sizes from 0.8B to 27B and answers bbox questions. Includes training, fine-tuning, inference, and evaluation. | [Try it](https://valen-team.github.io/) · [Playground](https://huggingface.co/spaces/Valen-Team/Valen-API) · [Docs & API](https://valen-team.github.io/docs/valen/) |
| **SDKs & integrations** | Call Valen-Decision from your own stack: the [Python SDK](https://github.com/Valen-Team/valen-sdk-python), the [JavaScript SDK](https://github.com/Valen-Team/valen-sdk-js), the [C++ text integration](https://github.com/Valen-Team/valen-sdk-cpp), an [agent skill](https://github.com/Valen-Team/skills) for Claude Code, Cursor and Codex, and [workflow integrations](https://github.com/Valen-Team/valen-integrations) for n8n, LangChain, Dify and Coze. | [ONNX & SDK guide](https://valen-team.github.io/docs/valen/onnx/) · [Cookbook](https://valen-team.github.io/cookbook/) |
| **[JevalKit](https://github.com/Valen-Team/JevalKit)** | An evaluation toolkit for Jev-like decision models, with unified model interfaces, prepared datasets, benchmark scoring, and a public leaderboard. | [Docs](https://valen-team.github.io/docs/jevalkit/) · [Leaderboard](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard) |
| **[Roller](https://github.com/Valen-Team/Roller)** | Agent trajectory collection across models and Harnesses. Runs tool-using agents such as Claude Code, Codex and OpenClaw in disposable Docker containers, grades benchmark tasks in the container where they ran, and stores the native session, a unified trace and SFT training data. Covers seven Harnesses and five benchmarks. | [Quick start](https://github.com/Valen-Team/Roller#quick-start) · [Docs](https://valen-team.github.io/roller/) · [PyPI](https://pypi.org/project/roller-agent/) |
| **[Awesome-RSI](https://github.com/Valen-Team/Awesome-RSI)** | A curated collection of papers, code, benchmarks, datasets, and models for recursive self-improvement, organized around experience accumulation, system modification, and model parameter updates. | [Papers](https://github.com/Valen-Team/Awesome-RSI#papers) · [Projects](https://github.com/Valen-Team/Awesome-RSI#projects) |

Our public projects cover decision models, evaluation, agent trajectory collection, and RSI research resources. We plan to expand the organization with more **agent and RSI projects**, sharing implementations, experiments, and reusable tools as they become available.

## Models, Datasets & Evaluation

**New:** [Valen-Decision-1.5](https://valen-team.github.io/news/valen-decision-1.5/) is released in five sizes, as native weights, ONNX and GGUF. Get it from the [Valen-Decision-1.5 collection](https://huggingface.co/collections/Valen-Team/valen-decision-15).

Browse all releases on [Hugging Face](https://huggingface.co/Valen-Team), or start with the [documentation](https://valen-team.github.io/docs/) to use Valen-Decision and run evaluations with JevalKit.

## The Name

**Valen** is named after evolutionary biologist **Leigh Van Valen**, who proposed the **Red Queen hypothesis**: organisms must continually adapt as the species around them evolve. Its literary inspiration comes from the Red Queen's race in *Through the Looking-Glass*.

For us, the name connects **speed with continuous evolution**: making decisions quickly while continuing to learn and adapt.

Our Chinese name, **万澜** (*Wàn Lán*), evokes countless waves in motion. The wave-shaped **V** in our logo carries that idea forward.

## Build With Us

We welcome contributions and collaboration across decision models, RSI, and agents:

- **Decision models and evaluation** — improve [Valen-Decision](https://github.com/Valen-Team/Valen), add models or benchmarks to [JevalKit](https://github.com/Valen-Team/JevalKit), or share data and reproducible results.
- **RSI research and methods** — contribute approaches to learning from experience, evolving agent systems, or updating models; suggest papers and implementations for [Awesome-RSI](https://github.com/Valen-Team/Awesome-RSI).
- **Agents and applications** — add Harnesses or benchmarks to [Roller](https://github.com/Valen-Team/Roller), contribute agent frameworks, tools, integrations, and applications, or propose new agent and RSI projects for the organization.

Open an issue or submit a pull request in the relevant repository. Documentation, examples, and translations are welcome too.
