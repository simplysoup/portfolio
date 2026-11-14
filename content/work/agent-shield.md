---
title: 'AgentShield: testing tool-using agents against injected instructions'
description: 'A synthetic prompt-injection lab with paired runs and explicit authorization.'
year: '2026'
number: 5
category: 'PUBLIC DEMO / AGENT SECURITY'
ownership: 'Independently developed'
status: 'Public repository; synthetic experimental lab, not production'
format: 'Engineering case study'
public: true
---
## The engineering question

An agent may need to read a document to complete a legitimate request. That document can also contain instructions from someone other than the user. I wanted to ask whether that lower-trust text could persuade an agent to perform a prohibited tool action, and how to distinguish a model ignoring an injection from a runtime refusing an attempted action.

AgentShield is an experimental lab for that question. It uses a synthetic workspace and records what happened in paired vulnerable and policy-enforced runs. It is not a production gateway, and its observations are not a measured defense rate. No real notification is sent in the demonstrated workspace.

## What I built

I built a runner that loads frozen JSONL attack fixtures and replays the same payload against both configurations. The vulnerable configuration deliberately bypasses runtime authorization. The policy configuration checks proposed actions at the tool boundary and records audit events. Keeping the configurations paired makes the payload itself comparable; it does not eliminate model variation or make a small sample representative.

The lab also supports exploratory adaptive attack generation. A generated payload can be unhelpful, or the attacker model can refuse; neither outcome should be counted as a successful defense. Frozen fixtures give me a stable replay path, while adaptive generation is a way to explore candidate attacks rather than evidence that every candidate works.

The synthetic tools simulate documents, records and effects in memory. The test task asks the defender to summarize a public revenue change without sending notifications. An injected instruction can try to redirect the agent toward a notification. The important boundary is the transition from text the agent reads to an action it proposes: content in a retrieved document is not authorization to use a tool.

The implementation includes tool-level authorization and audit events, alongside a deliberately vulnerable path for comparison. It also has 68 automated tests. Those tests exercise implementation behavior; they do not establish live model resistance across unknown attacks.

## How it was measured

The runner records exposure, proposed actions, policy decisions, synthetic side effects and whether the legitimate task completed. These fields have different meanings. An agent might never encounter the malicious material, might encounter it and ignore it, or might attempt an action that the policy denies. A trial with an error or without exposure should not be turned into a successful security result.

For frozen tests, I replay the identical fixture bytes in the paired configurations. The recorded payload hash allows the pairing to be checked. The default preloaded exposure puts the untrusted content in the defender prompt; that guarantees exposure in this setup but does not demonstrate a natural retrieval path. The repository also supports natural exposure, where a defender must actually retrieve the document.

The task-completion check is specific to the synthetic revenue task. It is not a general answer grader. I kept task completion separate from the unauthorized effect because an agent could complete the user's request and still do something forbidden along the way.

## Results

In the paired GPT-OSS 20B single-case demonstration, the vulnerable agent executed an unauthorized synthetic notification. The policy-configured agent ignored the injected instruction and did not attempt that call. Both completed the legitimate task. This is a useful trace of the distinction between configurations, but it is not a defense rate.

The policy run does not demonstrate authorization blocking an attempted call: the defender did not propose the prohibited call in that paired run. It would be incorrect to attribute the observed outcome to a policy denial. The README also describes a separate earlier unpaired policy denial; that should not be conflated with the paired observation.

The repository contains 12 candidate fixtures, not 12 confirmed exploits. They provide cases to evaluate, not a count of attacks that have succeeded. The automated tests offer regression coverage for the lab, while the live trace offers a narrow observation about one case and configuration pair. Neither substitutes for a broad evaluation.

## Limits & what this does not show

The workspace, notifications and data are synthetic. The experiment does not demonstrate real-world exfiltration, a production identity system or a deployed security gateway. Preloading the document establishes exposure but bypasses questions about retrieval. Model outputs can vary, and a vulnerable runtime does not mean every payload will succeed.

Policy enforcement and model resistance are separate claims. A model can ignore a payload without reaching the authorization boundary, and a policy can deny an attempted call even if the model follows malicious text. Meaningful comparisons require recording both the attempted action and the actual effect, as well as separating invalid trials and provider errors.

A broader study would need more diverse tasks, repeated trials and representative attacks, with the evaluation plan fixed in advance. This lab instead makes the trace and its limitations explicit so that a reader can see what was actually observed.

## Source

[Public AgentShield README, fixtures, implementation and tests ↗](https://github.com/simplysoup/agent-shield)
