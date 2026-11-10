import requests
import config

RUBRIC = (
    "You compare an ANSWER with a CONTEXT. "
    "Step 1: list every separate claim in the ANSWER, one per line, numbered. "
    "Step 2: for each claim, copy the sentence from the CONTEXT that states the same meaning, "
    "even if the words are different. If there is none, write NO SENTENCE FOUND for that claim. "
    "Step 3: count the claims that have NO SENTENCE FOUND. "
    "On the last line write only NO if that count is 1 or more, otherwise write only YES."
)

SICK = "Sick leave: Every full-time employee gets 15 sick days per year."
LEAVE = SICK + "\nNotice period: 30 days written notice.\nRemote work: 2 days a week.\nAnnual leave: 20 days per year."

CASES = [
    {"name": "faithful", "context": SICK, "answer": "You get 15 sick days per year.", "want": "SUPPORTED"},
    {"name": "wrong number", "context": SICK, "answer": "You get 12 sick days per year.", "want": "UNSUPPORTED"},
    {"name": "invented fact", "context": LEAVE, "answer": "Full-time employees are entitled to 3 days of bereavement leave.", "want": "UNSUPPORTED"},
    {"name": "refusal", "context": SICK, "answer": "I don't have that information.", "want": "SUPPORTED"},
    {"name": "faithful 2", "context": LEAVE, "answer": "Employees may work remotely 2 days a week.", "want": "SUPPORTED"},
    {"name": "faithful 3", "context": LEAVE, "answer": "You must give 30 days written notice.", "want": "SUPPORTED"},
    {"name": "faithful 4", "context": LEAVE, "answer": "You get 20 days of annual leave per year.", "want": "SUPPORTED"},
    {"name": "wrong remote", "context": LEAVE, "answer": "Employees may work remotely 4 days a week.", "want": "UNSUPPORTED"},
    {"name": "wrong notice", "context": LEAVE, "answer": "You must give 60 days written notice.", "want": "UNSUPPORTED"},
    {"name": "half true", "context": LEAVE, "answer": "You get 15 sick days per year, and unused days are paid out in cash.", "want": "UNSUPPORTED"},
    {"name": "outside fact", "context": LEAVE, "answer": "The capital of France is Paris.", "want": "UNSUPPORTED"},
    {"name": "paraphrase", "context": LEAVE, "answer": "Staff can work from home two days each week.", "want": "SUPPORTED"},
    {"name": "refusal 2", "context": LEAVE, "answer": "I don't have that information.", "want": "SUPPORTED"},
    {"name": "added condition", "context": LEAVE, "answer": "You get 15 sick days per year, but only after 6 months of service.", "want": "UNSUPPORTED"},
    {"name": "wrong unit", "context": LEAVE, "answer": "You must give 30 weeks written notice.", "want": "UNSUPPORTED"},
    {"name": "paraphrase 2", "context": LEAVE, "answer": "Full-time staff are entitled to 15 sick days each year.", "want": "SUPPORTED"},
    {"name": "paraphrase 3", "context": LEAVE, "answer": "Working remotely is allowed on 2 days per week.", "want": "SUPPORTED"},
    {"name": "paraphrase 4", "context": LEAVE, "answer": "Employees get 20 days off each year as annual leave.", "want": "SUPPORTED"},
    {"name": "wrong paraphrase", "context": LEAVE, "answer": "Staff can work from home five days each week.", "want": "UNSUPPORTED"},
    {"name": "two claims ok", "context": LEAVE, "answer": "You get 15 sick days per year, and 20 days of annual leave.", "want": "SUPPORTED"},
    {"name": "extra claim", "context": LEAVE, "answer": "You get 20 days of annual leave, and you can carry over 10 days.", "want": "UNSUPPORTED"},
    {"name": "wrong second", "context": LEAVE, "answer": "You must give 30 days notice and can work remotely 3 days a week.", "want": "UNSUPPORTED"},
    {"name": "refusal plus claim", "context": LEAVE, "answer": "I don't have that information, but you probably get 10 days.", "want": "UNSUPPORTED"},
]


def judge(context, answer):
    if "i don't have that information" in answer.lower():
        return "SUPPORTED", ""
    payload = {
        "model": config.JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": RUBRIC},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"},
        ],
        "stream": False,
        "options": {"temperature": 0},
    }
    response = requests.post(config.LLM_URL, json=payload, timeout=300)
    response.raise_for_status()
    text = response.json()["message"]["content"].upper()
    verdict = text.strip().split()[-1].strip(".:*!")
    stripped = answer.lower().replace("i don't have that information", "").strip(" .,!")
    if "i don't have that information" in answer.lower() and stripped == "":
        return "SUPPORTED", ""
    if verdict == "YES":
        return "SUPPORTED", text
    if verdict == "NO":
        return "UNSUPPORTED", text
    return "UNKNOWN", text


if __name__ == "__main__":
    correct = 0
    for case in CASES:
        got, raw = judge(case["context"], case["answer"])
        ok = got == case["want"]
        correct += ok
        print(f"{case['name']:<18} want={case['want']:<12} got={got:<12} {'OK' if ok else 'WRONG'}")
        if not ok:
            print("RAW:", repr(raw))
    print(f"\nJudge correct on {correct} of {len(CASES)}")