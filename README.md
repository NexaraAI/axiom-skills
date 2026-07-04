# Axiom Skills Registry

Skill manifests, bundles, and examples for [Axiom Agent](https://github.com/NexaraAI/axiom-agent).

## What is this?

Axiom Agent loads skill definitions from a registry. This repo is the official registry. It contains TOML manifests that describe what each skill does, when to use it, and what permissions it needs.

Axiom Agent fetches `registry.json` from this repo, reads the skill list, and installs manifests into the local config directory.

## Skills

Each skill has:
- `skill.toml`: the manifest with metadata, permissions, and an LLM card
- `README.md`: what the skill does
- `examples.json`: sample inputs and outputs

### Skill types

- **prompt**: guides the LLM with context and constraints. Does not execute code.
- **tool**: runs through a built-in Axiom executor (file.read, file.write, web.fetch, etc.).

External executable skills are not supported yet. All tool skills use built-in entrypoints.

### Current skills

| Skill | Type | Risk | Platforms |
|-------|------|------|-----------|
| file.read | tool | low | all |
| file.write | tool | medium | all |
| project.scan | tool | low | all |
| web.fetch | tool | medium | all |
| shell.powershell.safe | tool | high | windows |
| shell.bash.safe | tool | high | linux |
| shell.zsh.safe | tool | high | macos |
| git.status | tool | low | all |
| git.diff | tool | low | all |
| python.write | prompt | low | all |
| python.run | prompt | low | all |

## Bundles

Bundles group skills for a platform or use case.

| Bundle | Skills |
|--------|--------|
| essential.windows | file.read, file.write, project.scan, web.fetch, shell.powershell.safe, git.status, git.diff |
| essential.linux | file.read, file.write, project.scan, web.fetch, shell.bash.safe, git.status, git.diff |
| essential.macos | file.read, file.write, project.scan, web.fetch, shell.bash.safe, shell.zsh.safe, git.status, git.diff |
| coding.python | python.write, python.run, file.read, file.write, project.scan |
| coding.node | file.read, file.write, project.scan, shell.bash.safe |
| research.web | web.fetch, file.read, file.write |

Axiom installs the essential bundle for your OS during onboarding.

## Safety and Trust

Skills declare a risk level (low, medium, high) and required permissions. Axiom checks these before execution. Medium and high risk tools ask for terminal approval.

If a registry entry includes a `sha256` field, Axiom verifies the downloaded manifest before installing.

Custom registries print a trust warning. Installs from untrusted registries require confirmation.

## How Axiom installs skills

1. Fetch `registry.json` from the configured URL
2. Find the skill entry
3. Download the manifest from `manifest_url` (relative to registry root)
4. Verify SHA-256 if provided
5. Save to the local skills directory
6. Track in `installed_skills.json`

If the remote registry is unreachable and fallback is enabled, Axiom uses the bundled fixture registry from the main repo.

## Current status

This repo provides manifests, prompt cards, bundles, and examples. It does not contain executable code, compiled binaries, or external skill programs.

## Adding a skill

Create a directory under `skills/` with:
- `skill.toml` following the manifest format
- `README.md` with a short description
- `examples.json` with sample inputs and outputs

Add the skill entry to `registry.json` and optionally to a bundle.

## License

MIT

---

Docs cleaned using [Stop Slop](https://github.com/hardikpandya/stop-slop) style guidance.
