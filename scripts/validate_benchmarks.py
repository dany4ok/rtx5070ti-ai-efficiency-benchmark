#!/usr/bin/env python3
"""Validate benchmark submissions.

Checks structure and arithmetic only. Never marks a result as independently
verified, and never executes contributor code.
"""
import csv
import re
import sys

TOLERANCE = 0.10
MAX_TOKENS_PER_JOULE = 5.0

SUBMISSION_COLUMNS = [
    "gpu_model", "driver", "os", "model", "quantization", "engine",
    "engine_version", "power_limit_w", "clock_mhz", "avg_power_w",
    "output_tokens", "out_tok_s", "tokens_per_joule", "duration_s", "requests",
]
FORBIDDEN_COLUMNS = {
    "prompt", "prompts", "chat", "messages", "transcript", "api_key", "apikey",
    "credential", "credentials", "client", "client_id", "hostname", "host",
    "username", "user", "home_path", "session_id",
}
MEASUREMENT_COLUMNS = {"tokensout", "duration_s", "out_tok_s"}
SAMPLE_COLUMNS = {"powerw", "gpuload"}


def parse(value):
    if value is None:
        return None
    text = str(value).strip()
    if text in ("", "N/A", "NA", "n/a", "null"):
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def credential_like(text):
    return bool(re.search(r"sk-[A-Za-z0-9]{8,}", text)) or "Bearer " in text


def check_csv(path):
    problems, flags = [], []
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeDecodeError) as err:
        problems.append("INVALID: " + path + ": unreadable (" + str(err) + ")")
        return problems, flags
    if not rows:
        problems.append("INVALID: " + path + ": no rows")
        return problems, flags
    header = {name.strip().lower() for name in rows[0].keys() if name}
    leaked = sorted(header & FORBIDDEN_COLUMNS)
    if leaked:
        problems.append("INVALID: " + path + ": forbidden identifying columns " + ", ".join(leaked))
    submission = all(col in header for col in SUBMISSION_COLUMNS)
    measurement = MEASUREMENT_COLUMNS.issubset(header)
    samples = SAMPLE_COLUMNS.issubset(header)
    if not submission and not measurement and not samples:
        problems.append(
            "INVALID: " + path + ": unrecognized schema; submission columns needed are "
            + ", ".join(SUBMISSION_COLUMNS)
        )
        return problems, flags
    for index, row in enumerate(rows, start=1):
        if submission:
            tokens = parse(row.get("output_tokens"))
            duration = parse(row.get("duration_s"))
            power = parse(row.get("avg_power_w"))
            reported = parse(row.get("tokens_per_joule"))
            requests = parse(row.get("requests"))
            if tokens is None or tokens <= 0:
                problems.append("INVALID: " + path + " row " + str(index) + ": output_tokens missing or non-positive")
            if duration is None or duration <= 0:
                problems.append("INVALID: " + path + " row " + str(index) + ": duration_s missing or non-positive")
            if power is not None and power <= 0:
                problems.append("INVALID: " + path + " row " + str(index) + ": avg_power_w must be positive")
            if requests is not None and requests < 1:
                problems.append("INVALID: " + path + " row " + str(index) + ": requests must be at least 1")
            if tokens and duration and power:
                computed = tokens / (power * duration)
                if reported is None:
                    flags.append("FLAG: " + path + " row " + str(index) + ": tokens/J recalculated from raw measurements as " + format(computed, ".4f"))
                elif abs(computed - reported) / max(computed, reported) > TOLERANCE:
                    problems.append("INVALID: " + path + " row " + str(index) + ": reported tokens/J " + str(reported) + " disagrees with recalculated " + format(computed, ".4f"))
            if reported is not None and reported > MAX_TOKENS_PER_JOULE:
                flags.append("FLAG: " + path + " row " + str(index) + ": tokens/J " + str(reported) + " is implausibly high for this hardware class")
        elif measurement:
            tokens = parse(row.get("tokensOut"))
            duration = parse(row.get("duration_s"))
            rate = parse(row.get("out_tok_s"))
            if tokens is None or tokens < 0:
                problems.append("INVALID: " + path + " row " + str(index) + ": tokensOut missing")
            if duration is not None and duration <= 0:
                problems.append("INVALID: " + path + " row " + str(index) + ": duration_s must be positive")
            if rate is not None and rate <= 0:
                flags.append("FLAG: " + path + " row " + str(index) + ": out_tok_s " + str(rate) + " is zero or negative")
        else:
            power = parse(row.get("powerW"))
            if power is None:
                problems.append("INVALID: " + path + " row " + str(index) + ": powerW missing")
            elif power <= 0:
                flags.append("FLAG: " + path + " row " + str(index) + ": powerW " + str(power) + " is zero or negative")
    return problems, flags


SECTION_KEYS = {
    "avg_power_w": ("power consumption",),
    "output_tokens": ("output tokens",),
    "out_tok_s": ("tokens per second", "tok/s"),
    "tokens_per_joule": ("tokens per joule", "tokens/j"),
    "duration_s": ("duration",),
    "requests": ("requests",),
}


def check_issue(path):
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as err:
        return ["INVALID: issue unreadable (" + str(err) + ")"], []
    if credential_like(text):
        return ["INVALID: submission appears to contain a credential; redact it before submitting"], []
    sections = {}
    title = None
    body = []
    for line in text.splitlines():
        if line.startswith("###"):
            if title:
                sections[title.lower()] = "\n".join(body)
            title = line.lstrip("# ").strip()
            body = []
        else:
            body.append(line)
    if title:
        sections[title.lower()] = "\n".join(body)
    values = {}
    missing = []
    for key, words in SECTION_KEYS.items():
        found = None
        for heading, content in sections.items():
            if any(word in heading for word in words):
                match = re.search(r"\d[\d,.]*", content)
                if match:
                    found = parse(match.group(0))
                break
        if found is None:
            missing.append(key)
        else:
            values[key] = found
    problems, flags = [], []
    if missing:
        flags.append("FLAG: reported as N/A or missing: " + ", ".join(sorted(missing)))
    tokens = values.get("output_tokens")
    duration = values.get("duration_s")
    power = values.get("avg_power_w")
    reported = values.get("tokens_per_joule")
    if tokens is not None and tokens <= 0:
        problems.append("INVALID: output_tokens must be positive")
    if duration is not None and duration <= 0:
        problems.append("INVALID: duration must be positive")
    if power is not None and power <= 0:
        problems.append("INVALID: average power must be positive")
    if tokens and duration and power:
        computed = tokens / (power * duration)
        if reported is None:
            flags.append("FLAG: tokens/J recalculated from raw measurements as " + format(computed, ".4f"))
        elif abs(computed - reported) / max(computed, reported) > TOLERANCE:
            problems.append("INVALID: reported tokens/J " + str(reported) + " disagrees with recalculated " + format(computed, ".4f"))
        if reported is not None and reported > MAX_TOKENS_PER_JOULE:
            flags.append("FLAG: tokens/J " + str(reported) + " is implausibly high; needs manual review")
    return problems, flags


def main(argv):
    if argv and argv[0] == "--issue-file":
        problems, flags = check_issue(argv[1])
    else:
        problems, flags = [], []
        for path in argv:
            file_problems, file_flags = check_csv(path)
            problems.extend(file_problems)
            flags.extend(file_flags)
    for line in problems:
        print(line)
    for line in flags:
        print(line)
    print("VERIFICATION: self-measured; automation does not verify results independently.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
