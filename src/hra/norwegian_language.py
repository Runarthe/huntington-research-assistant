from __future__ import annotations

import re
from collections.abc import Mapping


NORWEGIAN_TERMINOLOGY: dict[str, str] = {
    "Huntington's disease": "Huntingtons sykdom",
    "Huntington disease": "Huntingtons sykdom",
    "huntingtin": "huntingtin",
    "mutant huntingtin": "mutant huntingtin",
    "gene silencing": "gendemping",
    "gene expression": "genuttrykk",
    "knockdown": "reduksjon av genuttrykk",
    "huntingtin lowering": "senking av huntingtin-nivået",
    "splicing": "spleising",
    "splicing modulator": "spleisemodulator",
    "molecular pathway": "molekylær signalvei",
    "molecular pathways": "molekylære signalveier",
    "pre- clinical animal models": "prekliniske dyremodeller",
    "pre-clinical animal models": "prekliniske dyremodeller",
    "future disease modifying treatments": "framtidige sykdomsmodifiserende behandlinger",
    "future disease-modifying treatments": "framtidige sykdomsmodifiserende behandlinger",
    "drug target": "målmolekyl for legemiddelutvikling",
    "drug targets": "målmolekyler for legemiddelutvikling",
    "pre-clinical": "preklinisk",
    "disease-modifying treatment": "sykdomsmodifiserende behandling",
    "disease-modifying treatments": "sykdomsmodifiserende behandlinger",
    "neuroprotective agents": "nevrobeskyttende forbindelser",
    "personalized medicine": "persontilpasset medisin",
    "stem cell therapy": "stamcelleterapi",
    "DNA methylation editing": "redigering av DNA-metylering",
    "DNA methylation": "DNA-metylering",
    "upstream": "oppstrøms",
    "downstream": "nedstrøms",
    "locus": "genområde (lokus)",
    "long-term": "langvarig",
    "attractive therapeutic approach": "mulig terapeutisk forskningsretning",
    "biomarker": "biomarkør",
    "neurofilament light": "lettkjede-nevrofilament (NfL)",
    "randomized controlled trial": "randomisert kontrollert studie",
    "placebo-controlled": "placebokontrollert",
    "open-label": "åpen studie",
    "adverse event": "uønsket hendelse",
    "confidence interval": "konfidensintervall",
    "animal model": "dyremodell",
    "cell model": "cellemodell",
    "in vitro": "i laboratorieforsøk utenfor en levende organisme (in vitro)",
    "in vivo": "i en levende organisme (in vivo)",
}

PROTECTED_IDENTIFIERS = (
    "HTT",
    "mHTT",
    "CAG",
    "HD",
    "NfL",
    "DNA",
    "RNA",
    "mRNA",
    "siRNA",
    "ASO",
    "ASOs",
    "CRISPR",
    "Cas9",
    "BDNF",
    "UHDRS",
)

NOT_STATED = "Not stated in the abstract."

_NUMBER_PATTERN = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?:\s*%)?")
_SECTION_LABEL_PATTERN = re.compile(
    r"\b(?:background|objective|methods|results|conclusions):\s*",
    re.IGNORECASE,
)
_PLACEHOLDER_PATTERN = re.compile(r"__HRA_(?:TERM|GLOSSARY)_\d+__")
_ADVICE_PATTERNS = (
    re.compile(r"\bdu bør\b", re.IGNORECASE),
    re.compile(r"\bpasient(?:er)? bør\b", re.IGNORECASE),
    re.compile(r"\banbefalt behandling\b", re.IGNORECASE),
    re.compile(r"\bbør behandles\b", re.IGNORECASE),
    re.compile(r"\bpasser for deg\b", re.IGNORECASE),
    re.compile(r"\b(?:attraktiv|effektiv|lovende) behandlingsmetode\b", re.IGNORECASE),
    re.compile(r"\bkan (?:kurere|stoppe|bremse) (?:Huntingtons sykdom|sykdommen)\b", re.IGNORECASE),
    re.compile(r"\bgir håp\b", re.IGNORECASE),
    re.compile(
        r"\bHTT\b[^.!?]{0,50}\b(?:den genetiske årsaken|årsaken til sykdommen)\b",
        re.IGNORECASE,
    ),
)


class SummaryIntegrityError(RuntimeError):
    """Raised when a generated Norwegian summary fails deterministic checks."""


def glossary_for_text(text: str) -> dict[str, str]:
    """Return only glossary entries that occur in the source text."""

    lowered = text.casefold()
    return {
        english: norwegian
        for english, norwegian in NORWEGIAN_TERMINOLOGY.items()
        if english.casefold() in lowered
    }


def glossary_prompt(glossary: Mapping[str, str]) -> str:
    if not glossary:
        return "Ingen termer fra den kuraterte ordlisten ble funnet."
    return "\n".join(
        f"- {english}: {norwegian}" for english, norwegian in glossary.items()
    )


def numeric_tokens(text: str) -> set[str]:
    return {
        match.group(0).replace(" ", "").replace(",", ".")
        for match in _NUMBER_PATTERN.finditer(text)
    }


def protected_identifiers(text: str) -> set[str]:
    found: set[str] = set()
    for identifier in PROTECTED_IDENTIFIERS:
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(identifier)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        if pattern.search(text):
            found.add(identifier)
    return found


def facts_as_text(facts: Mapping[str, str]) -> str:
    return "\n".join(facts.values())


def _normalized_text(value: str) -> str:
    without_labels = _SECTION_LABEL_PATTERN.sub(" ", value)
    return " ".join(without_labels.casefold().split())


def protect_glossary_for_translation(
    facts: Mapping[str, str],
    glossary: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Replace known English biomedical phrases with fixed Norwegian placeholders."""

    protected = dict(facts)
    replacements: dict[str, str] = {}
    for index, (english, norwegian) in enumerate(
        sorted(glossary.items(), key=lambda item: (-len(item[0]), item[0]))
    ):
        pattern = re.compile(re.escape(english), re.IGNORECASE)
        if not any(pattern.search(value) for value in protected.values()):
            continue
        placeholder = f"__HRA_GLOSSARY_{index}__"
        replacements[placeholder] = norwegian
        protected = {
            name: pattern.sub(placeholder, value)
            for name, value in protected.items()
        }
    return protected, replacements


def protect_identifiers_for_translation(
    facts: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Replace scientific identifiers with stable placeholders for the LLM call."""

    protected = dict(facts)
    replacements: dict[str, str] = {}
    present = protected_identifiers(facts_as_text(facts))
    for index, identifier in enumerate(
        sorted(present, key=lambda value: (-len(value), value))
    ):
        placeholder = f"__HRA_TERM_{index}__"
        replacements[placeholder] = identifier
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(identifier)}(?![A-Za-z0-9])"
        )
        protected = {
            name: pattern.sub(placeholder, value)
            for name, value in protected.items()
        }
    return protected, replacements


def restore_identifier_placeholders(
    sections: Mapping[str, str],
    replacements: Mapping[str, str],
) -> dict[str, str]:
    """Restore protected identifiers or reject a mutated placeholder."""

    restored = dict(sections)
    combined = facts_as_text(restored)
    missing = [placeholder for placeholder in replacements if placeholder not in combined]
    unknown = [
        placeholder
        for placeholder in _PLACEHOLDER_PATTERN.findall(combined)
        if placeholder not in replacements
    ]
    if missing or unknown:
        raise SummaryIntegrityError(
            "Den lokale modellen endret en beskyttet fagidentifikator."
        )
    for placeholder, identifier in replacements.items():
        restored = {
            name: value.replace(placeholder, identifier)
            for name, value in restored.items()
        }
    return restored


def validate_facts_against_source(facts: Mapping[str, str], source: str) -> None:
    """Reject fact excerpts that cannot be traced directly to the source."""

    fact_text = facts_as_text(facts)
    normalized_source = _normalized_text(source)
    unsupported_sections = [
        name
        for name, excerpt in facts.items()
        if excerpt != NOT_STATED
        and _normalized_text(excerpt) not in normalized_source
    ]
    unsupported_numbers = numeric_tokens(fact_text) - numeric_tokens(source)
    unsupported_identifiers = protected_identifiers(fact_text) - protected_identifiers(
        source
    )
    if unsupported_sections or unsupported_numbers or unsupported_identifiers:
        raise SummaryIntegrityError(
            "Faktagrunnlaget inneholder tekst, tall eller fagidentifikatorer som ikke kan spores direkte til kilden."
        )


def validate_norwegian_summary(
    facts: Mapping[str, str],
    summary: str,
    source: str,
) -> None:
    """Ensure the Norwegian rendering preserves selected facts and safety limits."""

    fact_text = facts_as_text(facts)
    fact_numbers = numeric_tokens(fact_text)
    summary_numbers = numeric_tokens(summary)
    if not fact_numbers.issubset(summary_numbers) or not summary_numbers.issubset(
        numeric_tokens(source)
    ):
        raise SummaryIntegrityError(
            "Den norske teksten endret, utelot eller la til tall uten kildegrunnlag."
        )

    expected_identifiers = protected_identifiers(fact_text)
    summary_identifiers = protected_identifiers(summary)
    if not expected_identifiers.issubset(summary_identifiers) or not summary_identifiers.issubset(
        protected_identifiers(source)
    ):
        raise SummaryIntegrityError(
            "Den norske teksten endret, utelot eller la til fagidentifikatorer uten kildegrunnlag."
        )
    for identifier in summary_identifiers:
        if not re.search(
            rf"(?<![A-Za-z0-9]){re.escape(identifier)}(?![A-Za-z0-9])",
            summary,
        ):
            raise SummaryIntegrityError(
                "Den norske teksten endret store eller små bokstaver i en fagidentifikator."
            )

    if any(pattern.search(summary) for pattern in _ADVICE_PATTERNS):
        raise SummaryIntegrityError(
            "Den norske teksten inneholder formuleringer som kan oppfattes som helseråd."
        )
