# Frozen development lessons, version 1

These rules were curated with Codex assistance from official training runs.
They contain no task answers and are not updated during held-out evaluation.

## L1: Stop searching after confirming an unavailable external dataset

When execution fails on a network request, inspect the loader and check the
provided data directory once. If the required dataset is neither bundled nor
cached, record the failing request and submit unanswered values with blocker
evidence. Do not repeatedly search the entire filesystem or try alternative
internet endpoints in an offline environment.

Source: development capsule-4098236, run
20261117T200334263866Z-capsule-4098236-run-A1, artifacts/step-003.stdout.txt
(network failure), step-004.stdout.txt (loader), and step-007.stdout.txt
(repeated broad search). The run eventually exceeded its context bound.

## L2: Execute a notebook once and inspect its structured outputs

For notebook reproduction, save an executed notebook in the results directory,
then render that executed notebook to the requested presentation format. Locate
relevant output cells using the requested metric labels. Print only the needed
output segments. Avoid dumping full notebook source or raw HTML into context,
and avoid executing the whole experiment again merely to read its output.

Source: development capsule-0940461, run
20261117T200757054830Z-capsule-0940461-run-A1, tool steps 003 through 010.
Source dumping and repeated executions preceded a context-limit failure.

## L3: Discover documentation filenames before chaining commands

List the task directory before assuming that README.md exists. Read whichever
instruction file is actually provided and read REPRODUCING.md separately. A
missing optional README should not prevent required instructions from being read.

Source: development capsule-9168639, run
20261117T200518810509Z-capsule-9168639-run-A1, step-001 and step-002.
The first chained command stopped at a missing README; the next inspected the
available files and recovered.

## Scope

These are development-derived workflow heuristics, not verified universal rules.
They may reduce wasted calls without improving final accuracy. Report both cost
and accuracy, and preserve any adverse effects.
