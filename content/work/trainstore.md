---
title: 'TrainStore: measuring storage for training and checkpoints'
description: 'A storage lab for PyTorch data loading, checkpoint publication and recovery.'
year: '2026'
number: 4
category: 'PUBLIC DEMO / SYSTEMS'
ownership: 'Independently developed'
status: 'Public repository; experimental lab, not production'
format: 'Engineering case study'
public: true
---
## The engineering question

A training process needs more than a place to put files. It needs to read data fast enough to keep the model working, publish checkpoints without exposing partial state, and recover after interruptions. I wanted to understand those properties together, rather than treating a successful upload as proof that training storage was reliable.

TrainStore is a lab for comparing an object path and a mounted filesystem path. I built the experiment code and checkpoint clients around existing storage and infrastructure components. I did not build S3, Valkey, JuiceFS, k3s, SILO or Prometheus; I integrated them. The result is a lab that measures honestly, not a production claim.

## What I built

I deployed k3s in short bursts on three on-demand EC2 hosts, each with two vCPUs, across two availability zones in us-east-2. I tore the environment down after the experiments. S3 held objects; JuiceFS Community Edition exposed a POSIX interface through CSI, with ElastiCache Serverless Valkey holding filesystem metadata. The object and filesystem paths have different semantics, so they should not be treated as interchangeable merely because both ultimately store bytes.

The checkpoint protocol writes data under versioned keys and publishes a manifest as its atomic commit point. Conditional writes using If-Match and If-None-Match prevent a stale publisher from replacing a newer manifest. Retries are idempotent; a stale writer receives StaleCheckpointError. A sweep retains the last two checkpoints. The manifest is the state that tells a reader which checkpoint is committed, not a promise that every interrupted upload left no unused objects.

I wrote a Go standard-library-only S3 client, including SigV4 signing, and a CheckpointStore compatible with the Python implementation at the byte level. The clients interoperate in both directions. That made compatibility an observable behavior across implementations rather than an assumption based on shared names.

## How it was measured

The training workload used CIFAR-10, ResNet-18 and AdamW for 16 steps with seed 1234. I compared loader wait and throughput across paths and worker settings, and distinguished a genuinely cold filesystem mount from a warm read. I also measured checkpoint publication, reading and resume, and injected interruptions to see whether readers saw torn data or violated monotonicity.

The protocol has 12 offline tests; live suites exercised real S3 and SILO. During live testing I found that a writer killed mid-publish could destroy the last good checkpoint. I fixed that bug and covered the corrected protocol. A separate live PUT exposed a signing bug: unsigned x-amz-* headers were rejected. Fixing the signer mattered because an offline fake alone could not establish real service interoperability.

## Results

Single-threaded S3 spent 85% of time waiting for data and delivered 33 samples per second. POSIX with two workers spent 5% waiting and delivered about 197 samples per second. Cache state made a material difference: true-cold POSIX measured 28 samples per second and 87% wait, versus warm at 123 samples per second and 46% wait. These are observations under the stated workload, not universal filesystem rankings.

A 133.9 MiB checkpoint published in 4.4 seconds, or 31 MiB/s, and read in 1.6 seconds, or 82 MiB/s. Resume was bit-exact in this test: step-9 loss matched and maximum absolute weight difference was 0.0. A cross-availability-zone eviction and remount retained a sentinel file. Under node interruption, 235 writes and 291 reads produced no torn reads or monotonicity violations. JuiceFS cache median read latency moved from 8.5 ms to 1.9 ms.

Each observation answers a different question. The checkpoint timing measures transfer in this setup; the resume comparison checks state continuity; the interruption exercise checks what the tested reader observed. None by itself proves a service-level guarantee.

## Limits & what this does not show

There is no replication by design. The deployment used one region, CPU-only training and a 10,000-image dataset. The two-vCPU host is a ceiling on the reported S3 loader numbers, so those figures should not be generalized to larger machines or GPU training. Cache warmth, access pattern and worker count all change the comparison. Cross-zone remount is useful evidence about this exercise, not proof of independent hardware fault tolerance or availability under every failure.

The bug found during live testing is also a reason to distinguish a tested implementation from a protocol sketch. The offline suite covers known cases, while the live services expose behavior the fake does not reproduce. More workloads, longer runs and independent failure domains would be needed before using these results to choose a production design.

## Source

[Public TrainStore README, code, experiments and results ↗](https://github.com/simplysoup/trainstore)
