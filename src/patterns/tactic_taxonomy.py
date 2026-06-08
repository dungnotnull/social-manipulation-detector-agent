from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TacticCategory(str, Enum):
    PSYCHOLOGICAL = "A"
    COORDINATED = "B"
    FINANCIAL = "C"
    DISINFORMATION = "D"
    LLM_PATTERNS = "E"


@dataclass
class Tactic:
    name: str
    category: TacticCategory
    description: str
    detection_difficulty: str
    keywords: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    false_positive_risk: str = "MEDIUM"


TACTICS: dict[str, Tactic] = {
    # Category A — Psychological Influence
    "SOCIAL_PROOF": Tactic(
        name="SOCIAL_PROOF",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Manufactured consensus — 'Everyone is doing this', fake testimonials, bot-driven likes/upvotes to simulate popularity.",
        detection_difficulty="MEDIUM",
        keywords=["everyone is", "thousands have", "the community agrees", "people are saying", "everyone knows"],
        false_positive_risk="MEDIUM",
    ),
    "URGENCY_SCARCITY": Tactic(
        name="URGENCY_SCARCITY",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Artificial time pressure — countdowns, limited-time offers, FOMO triggers to short-circuit deliberation.",
        detection_difficulty="LOW",
        keywords=["only today", "last chance", "act now", "before it's too late", "don't miss out", "limited time"],
        false_positive_risk="LOW",
    ),
    "AUTHORITY_FABRICATION": Tactic(
        name="AUTHORITY_FABRICATION",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Fake expert citations, manufactured credentials, unverifiable insider claims.",
        detection_difficulty="HIGH",
        keywords=["according to research", "experts agree", "insider info", "scientists say", "studies show"],
        false_positive_risk="HIGH",
    ),
    "RECIPROCITY_TRAP": Tactic(
        name="RECIPROCITY_TRAP",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Creating obligation — 'I shared this with you, now you must...'",
        detection_difficulty="HIGH",
        keywords=["i shared this", "after all i've done", "you owe it to yourself"],
        false_positive_risk="HIGH",
    ),
    "LIKING_FLATTERY": Tactic(
        name="LIKING_FLATTERY",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Excessive agreement + flattery before persuasion attempt.",
        detection_difficulty="MEDIUM",
        keywords=["you seem smart", "as a fellow", "you're clearly intelligent"],
        false_positive_risk="HIGH",
    ),
    "COMMITMENT_ESCALATION": Tactic(
        name="COMMITMENT_ESCALATION",
        category=TacticCategory.PSYCHOLOGICAL,
        description="Small ask → bigger ask across comment chain. Requires thread-level analysis.",
        detection_difficulty="HIGH",
        keywords=[],
        false_positive_risk="HIGH",
    ),

    # Category B — Coordinated Inauthentic Behavior
    "NARRATIVE_FLOODING": Tactic(
        name="NARRATIVE_FLOODING",
        category=TacticCategory.COORDINATED,
        description="Repeating same talking points with slight variations across accounts/comments.",
        detection_difficulty="MEDIUM",
        keywords=[],
        false_positive_risk="MEDIUM",
    ),
    "BANDWAGON_MANUFACTURING": Tactic(
        name="BANDWAGON_MANUFACTURING",
        category=TacticCategory.COORDINATED,
        description="Creating illusion of consensus through coordinated bot posting.",
        detection_difficulty="MEDIUM",
        keywords=[],
        false_positive_risk="MEDIUM",
    ),
    "ASTROTURFING": Tactic(
        name="ASTROTURFING",
        category=TacticCategory.COORDINATED,
        description="Fake grassroots support — organic-seeming language with corporate/state coordination.",
        detection_difficulty="HIGH",
        keywords=[],
        false_positive_risk="HIGH",
    ),
    "HASHTAG_BOMBING": Tactic(
        name="HASHTAG_BOMBING",
        category=TacticCategory.COORDINATED,
        description="Off-topic hashtag injection to hijack trending topics for manipulation.",
        detection_difficulty="LOW",
        keywords=[],
        false_positive_risk="LOW",
    ),

    # Category C — Financial Manipulation
    "FOMO_PUMP": Tactic(
        name="FOMO_PUMP",
        category=TacticCategory.FINANCIAL,
        description="Price prediction + urgency + social proof combo to create artificial buying pressure.",
        detection_difficulty="LOW",
        keywords=["to the moon", "100x", "10x", "about to explode", "whales are accumulating", "don't miss this coin"],
        false_positive_risk="LOW",
    ),
    "FUD_DUMP": Tactic(
        name="FUD_DUMP",
        category=TacticCategory.FINANCIAL,
        description="Fear amplification to trigger panic selling — coordinated negative narrative.",
        detection_difficulty="MEDIUM",
        keywords=["crash", "sell now", "exit scam", "rug pull", "protect your capital", "get out while you can"],
        false_positive_risk="MEDIUM",
    ),
    "SHILL_PATTERN": Tactic(
        name="SHILL_PATTERN",
        category=TacticCategory.FINANCIAL,
        description="Unprompted promotion, referral links, fake testimonials.",
        detection_difficulty="LOW",
        keywords=["dm me", "join my group", "use my code", "referral link", "i turned"],
        false_positive_risk="LOW",
    ),
    "WHALE_NARRATIVE": Tactic(
        name="WHALE_NARRATIVE",
        category=TacticCategory.FINANCIAL,
        description="Unverifiable claims about whale/institutional accumulation to drive FOMO.",
        detection_difficulty="MEDIUM",
        keywords=["whales are buying", "institutional money", "smart money", "insider buying"],
        false_positive_risk="MEDIUM",
    ),

    # Category D — Disinformation
    "EMOTIONAL_HIJACKING": Tactic(
        name="EMOTIONAL_HIJACKING",
        category=TacticCategory.DISINFORMATION,
        description="Extreme emotional language (outrage, fear, hope) to bypass critical thinking.",
        detection_difficulty="MEDIUM",
        keywords=["outrageous", "unbelievable", "shocking", "you won't believe", "this changes everything"],
        false_positive_risk="MEDIUM",
    ),
    "FALSE_DILEMMA": Tactic(
        name="FALSE_DILEMMA",
        category=TacticCategory.DISINFORMATION,
        description="Forced binary choice — 'Either you X or you're a [enemy]'. Eliminates nuance.",
        detection_difficulty="LOW",
        keywords=["either you", "anyone who disagrees", "you're either with us", "if you're not"],
        false_positive_risk="LOW",
    ),
    "FIREHOSE_FALSEHOOD": Tactic(
        name="FIREHOSE_FALSEHOOD",
        category=TacticCategory.DISINFORMATION,
        description="Multiple false claims at once — too many to fact-check in real time.",
        detection_difficulty="HIGH",
        keywords=[],
        false_positive_risk="HIGH",
    ),
    "CONTEXT_REMOVAL": Tactic(
        name="CONTEXT_REMOVAL",
        category=TacticCategory.DISINFORMATION,
        description="Real quote/statistic stripped of context to mislead.",
        detection_difficulty="HIGH",
        keywords=[],
        false_positive_risk="HIGH",
    ),

    # Category E — LLM-Characteristic Patterns
    "LLM_HOLLOW_AFFIRMATION": Tactic(
        name="LLM_HOLLOW_AFFIRMATION",
        category=TacticCategory.LLM_PATTERNS,
        description="Excessive agreement without substance — 'Absolutely!', 'Great point!', 'You're so right!'",
        detection_difficulty="LOW",
        keywords=["absolutely", "great point", "you're so right", "certainly", "great question"],
        false_positive_risk="MEDIUM",
    ),
    "LLM_OVER_HEDGING": Tactic(
        name="LLM_OVER_HEDGING",
        category=TacticCategory.LLM_PATTERNS,
        description="Excessive qualifications in informal contexts — 'It's important to note that...'",
        detection_difficulty="LOW",
        keywords=["it's important to note", "it's worth considering", "one might argue", "that said"],
        false_positive_risk="MEDIUM",
    ),
    "LLM_TEMPLATE_STRUCTURE": Tactic(
        name="LLM_TEMPLATE_STRUCTURE",
        category=TacticCategory.LLM_PATTERNS,
        description="Numbered lists and bullet points in casual social conversation.",
        detection_difficulty="LOW",
        keywords=[],
        false_positive_risk="HIGH",
    ),
    "LLM_BALANCED_FAKEOUT": Tactic(
        name="LLM_BALANCED_FAKEOUT",
        category=TacticCategory.LLM_PATTERNS,
        description="Fake 'both sides' framing before pushing one agenda.",
        detection_difficulty="MEDIUM",
        keywords=["on one hand", "while there are valid points on both sides", "it's true that"],
        false_positive_risk="HIGH",
    ),
}


def get_tactics_by_category(category: TacticCategory) -> list[Tactic]:
    return [t for t in TACTICS.values() if t.category == category]


def get_all_tactic_names() -> list[str]:
    return list(TACTICS.keys())
