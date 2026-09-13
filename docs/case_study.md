# SentinelIP: Classifying Malicious IP Addresses from Network Metadata

The core question I set out to answer: **can you tell whether an IP address is malicious using only network metadata — country, ISP, hosting/proxy/mobile status — without ever letting the model see an existing risk score?**

## What it does

SentinelIP pulls two independent pieces of information for ~600 IP addresses:

- **AbuseIPDB** gives the label — whether an IP has been reported as malicious (confidence score ≥75, reported within the last 90 days), or is clean.
- **ip-api.com** gives the features — country, ISP, network organization, and whether the IP is a hosting server, a known proxy, or on a mobile connection.

I deliberately kept these two sources separate. AbuseIPDB's own confidence score never goes into the model as an input — only as the answer key. The point was to see whether a model could learn the *pattern* of what malicious infrastructure looks like, rather than just parroting back a number it was handed.

For the benign side of the dataset, I didn't just grab safe-looking IPs at random. Early on, I ran a quick check on the malicious sample and found that only about 56% of malicious IPs were hosting-provider infrastructure (AWS, cloud servers, etc.) — the rest looked residential, likely compromised home devices. So I built the benign set to mirror that same mix: roughly 170 IPs from AWS/Google/Cloudflare ranges, and about 130 from real residential ISP ranges (Comcast, AT&T, Airtel, Jio), pulled via RIPE's public ASN lookup service. It felt important that the benign side wasn't just "the opposite of malicious" in some lazy way — it needed to represent normal internet traffic honestly, including the fact that most people's home connections look nothing like a data center.

Everything landed in PostgreSQL, got queried with SQL to find real patterns, then went through two classification models — Logistic Regression and Random Forest — before ending up as a Tableau dashboard. Both models are trained and compared side by side rather than picking one and discarding the other, since each turned out to have a genuine strength worth keeping visible (more on that below).

## What the data actually showed

A few findings genuinely surprised me:

**Hosting status is a weak signal on its own.** 53% of malicious IPs were hosting infrastructure, versus 47% of benign ones — barely a difference, since my benign set intentionally included plenty of legitimate cloud servers too.

**Proxy and mobile status pull in opposite directions.** Malicious IPs were more than twice as likely to be flagged as a known proxy (16% vs 7%). Mobile went the other way — only 4% of malicious IPs were mobile, compared to 11% of benign ones. That makes sense once you think about it from an attacker's perspective: mobile connections are unreliable, capped, and easy to trace back to a real SIM — bad infrastructure for running anything sustained. A rented cloud server is a much better tool for the job.

**The combination of hosting AND proxy together was the standout finding.** Individually, hosting and proxy were each only moderate signals. Together, IPs that were both hosting *and* proxy showed a 97% malicious rate — dramatically higher than either flag alone. That one number ended up shaping a real feature engineering decision later.

**Country and ISP risk numbers need an honest caveat.** Countries like Russia and Bulgaria initially showed a 100% malicious rate in my early analysis — but on closer inspection, that was mostly an artifact of how I built the benign dataset (heavily US/India-weighted), not a genuine finding. Once I filtered to countries with a large enough sample size, a more trustworthy picture emerged: China, Germany, France, and the Netherlands showed consistently high malicious rates (75-96%) even with reasonable sample sizes, while the US and India sat much lower — mostly because that's exactly where I'd deliberately sourced most of the benign traffic from. I think this is one of the more important parts of the whole project: knowing *why* your own numbers look the way they do, instead of just reporting them.

## The model, and a decision I had to actually defend to myself

I trained a Logistic Regression baseline and a Random Forest, and tuned the decision threshold for both — moving it from the default 0.5 down to 0.3.

At first this felt backwards. The 0.5 threshold had better accuracy (92% vs 88%) and better precision (92% vs 83%) than 0.3. On paper, 0.5 is the "better" model. But accuracy treats every mistake the same, and in this context, the two kinds of mistakes aren't the same at all — missing a real malicious IP is a genuinely bad outcome, while a false alarm just costs someone a few minutes double-checking something that turned out fine. Lowering the threshold to 0.3 meant catching 3 more real threats out of 60, at the cost of 7 more false alarms. I went with 0.3, and could explain exactly why once I'd actually argued myself out of just taking the higher-scoring option.

Random Forest edged out Logistic Regression on recall (97% vs 95%), and its feature importances backed up what the SQL analysis had already found — hosting and the engineered hosting-and-proxy combination both ranked near the top. But when I ran 5-fold cross-validation to check how stable that result really was, Random Forest's recall swung between 70% and 97% depending on which slice of data it saw, while Logistic Regression stayed steady in the mid-80s across every fold. With only ~600 rows to work with, that's a real tradeoff, not a rounding error — Random Forest wins on paper but is meaningfully less predictable, and I'd rather be upfront about that than just report the headline number.

## What I'd do differently with more time

- Source benign IPs from a wider set of countries, not just the US and India, so country-level risk comparisons aren't distorted by where I happened to pull "safe" traffic from.
- Dig into why the "everything outside my top 10 ISPs" bucket turned out to be the single strongest predictor in the Random Forest — it suggests there's real signal in the long tail of small, obscure hosting providers that a top-N grouping approach doesn't fully capture.
- Grow the dataset past 600 rows — Random Forest's instability across cross-validation folds is very likely a small-data problem, and I'd want to see if it resolves with more examples before trusting it in place of the simpler model.

## Tools used

Python (requests, pandas, scikit-learn) · PostgreSQL · SQL · Tableau · Logistic Regression · Random Forest · AbuseIPDB API · ip-api.com · RIPEstat
