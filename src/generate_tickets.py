"""
Generates synthetic support tickets for Alpine Trail Co, a fictional
mountain bike e-commerce + guided tour booking company.

Tickets are seeded with the P1-P4 trigger vocabulary the rules engine
(Phase 3) will match against, so this dataset is a reliable baseline
to build and test rules against.
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

SERVICES = [
    "checkout",
    "inventory",
    "bike-builder",
    "tour-booking",
    "account",
    "shipping",
    "mobile-app",
]
TICKET_TEMPLATES = {
    "P1": [
        (
            "{service} is down, customers can't check out",
            "Multiple customers reporting {service} is down. Checkout is "
            "down and no orders are going through. This is affecting all "
            "customers right now.",
        ),
        (
            "Payment processor down, can't process payments",
            "Our payment processor is down. Checkout is throwing a 500 "
            "error on checkout for every attempt. Unable to place any "
            "orders since this started.",
        ),
    ],
    "P2": [
        (
            "{service} is crashing for some users",
            "The {service} tool is crashing intermittently. Support has "
            "gotten several reports this morning, seems to affect maybe "
            "a third of attempts.",
        ),
        (
            "Tour bookings failing for weekend slots",
            "Tour bookings failing when customers try to book weekend "
            "slots. Can't complete booking past the confirmation step.",
        ),
        (
            "Shipping labels not generating",
            "Warehouse team says shipping labels not generating for "
            "orders placed in the last two hours. Orders stuck in "
            "processing.",
        ),
    ],
    "P3": [
        (
            "{service} slow to load",
            "{service} takes a long time to load, sometimes times out on "
            "the first attempt. Reloading usually fixes it.",
        ),
        (
            "Images not displaying on {service}",
            "Product images not displaying correctly on {service}. "
            "Occasionally fails to load thumbnails, intermittent error, "
            "not consistent.",
        ),
    ],
    "P4": [
        (
            "Password reset email delayed",
            "Customer says password reset email delayed by about 20 "
            "minutes. Eventually arrived, just slow.",
        ),
        (
            "Typo on {service} page",
            "Minor display issue: typo on the {service} product "
            "description page. Says 'recieve' instead of 'receive'.",
        ),
        (
            "Profile picture not updating",
            "One customer says their profile picture not updating after "
            "upload on {service}. Cosmetic only, account still works "
            "fine.",
        ),
        (
            "Feature request for {service}",
            "Customer would like to request a wishlist feature on "
            "{service}. Not urgent, just a suggestion.",
        ),
    ],
}

SEVERITY_WEIGHTS = {"P1": 0.05, "P2": 0.15, "P3": 0.30, "P4": 0.50}

STATUSES = ["open", "resolved", "closed"]
STATUS_WEIGHTS = [0.2, 0.3, 0.5]


def random_timestamp(days_back=90):

    now = datetime.utcnow()
    day_offset = random.randint(0, days_back)
    dt = now - timedelta(days=day_offset)

    # Bias toward business hours (8am-6pm)
    hour = random.choices(
        range(24),
        weights=[1] * 8 + [4] * 10 + [1] * 6,
    )[0]
    minute = random.randint(0, 59)
    dt = dt.replace(hour=hour, minute=minute, second=random.randint(0, 59))

    # Slightly fewer tickets on weekends
    if dt.weekday() >= 5 and random.random() < 0.5:
        dt -= timedelta(days=1)

    return dt


def generate_ticket(index):
    severity = random.choices(
        list(SEVERITY_WEIGHTS.keys()),
        weights=list(SEVERITY_WEIGHTS.values()),
    )[0]

    service = random.choice(SERVICES)
    title_template, body_template = random.choice(TICKET_TEMPLATES[severity])

    title = title_template.format(service=service)
    body = body_template.format(service=service)

    created_at = random_timestamp()
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]

    ticket = {
        "external_id": f"ATC-{10000 + index}",
        "source": "synthetic",
        "created_at": created_at.isoformat() + "Z",
        "title": title,
        "body": body,
        "service": service,
        "status": status,
        "_seed_severity": severity,
    }
    return ticket


def main(count=500, output_path="tickets.json"):
    tickets = [generate_ticket(i) for i in range(count)]
    tickets.sort(key=lambda t: t["created_at"])

    with open(output_path, "w") as f:
        json.dump(tickets, f, indent=2)

    print(f"Generated {count} tickets -> {output_path}")

    # Quick sanity check on the distribution
    from collections import Counter
    counts = Counter(t["_seed_severity"] for t in tickets)
    for sev in ["P1", "P2", "P3", "P4"]:
        print(f"  {sev}: {counts[sev]}")


if __name__ == "__main__":
    main()