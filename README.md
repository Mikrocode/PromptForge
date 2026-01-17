# PromptForge

PromptForge is a non-AI tool for people who work with AI prompts seriously.

It treats prompts as specifications, not chat messages.

PromptForge lets you:
- write prompts with enforced structure and clear constraints
- validate prompts for contradictions, ambiguity, and missing requirements
- lint prompts using strict, opinionated rules
- version prompts and inspect changes with clear diffs

The goal is simple: reduce vague prompts, prevent drift, and make prompt behavior predictable.

PromptForge does not generate content.
It does not suggest prompts.
It judges them.

Prompts in. Discipline out.

## Quick start

```bash
python -m promptforge lint examples/example_prompt.txt
```

## Example output

```text
$ promptforge lint examples/example_prompt.txt
ERROR [PF002] line 2: Vague verb 'Improve' found; be specific.
ERROR [PF002] line 2: Vague verb 'better' found; be specific.
ERROR [PF003] line 1: Contradictory constraints: concise and detailed requirements conflict.
ERROR [PF004] line 1: Missing audience definition (who the prompt is for).
```
