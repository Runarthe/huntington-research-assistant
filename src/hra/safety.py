MEDICAL_DISCLAIMERS = {
    "en": (
        "This tool is for educational and research navigation purposes only. "
        "It is not medical advice. Always consult qualified healthcare professionals "
        "for diagnosis, treatment, or genetic counselling."
    ),
    "no": (
        "Dette verktøyet er kun for læring og navigasjon i forskning. "
        "Det er ikke medisinsk rådgivning. Kontakt alltid kvalifisert helsepersonell "
        "for diagnose, behandling eller genetisk veiledning."
    ),
}

SUMMARY_DISCLAIMERS = {
    "en": (
        "Educational summary only. It may be incomplete or inaccurate and must not "
        "be used for medical decisions."
    ),
    "no": (
        "Kun en pedagogisk oppsummering. Den kan være ufullstendig eller unøyaktig "
        "og må ikke brukes til medisinske beslutninger."
    ),
}

PROHIBITED_GUIDANCE_MESSAGES = {
    "en": (
        "The app cannot provide diagnosis, treatment recommendations, personalized "
        "health guidance, or interpretation of personal medical situations."
    ),
    "no": (
        "Appen kan ikke gi diagnose, behandlingsanbefalinger, personlig helsehjelp "
        "eller tolke en enkeltpersons medisinske situasjon."
    ),
}

MEDICAL_DISCLAIMER = MEDICAL_DISCLAIMERS["en"]
SUMMARY_DISCLAIMER = SUMMARY_DISCLAIMERS["en"]
PROHIBITED_GUIDANCE = PROHIBITED_GUIDANCE_MESSAGES["en"]


def medical_disclaimer(language: str = "en") -> str:
    return MEDICAL_DISCLAIMERS.get(language, MEDICAL_DISCLAIMERS["en"])


def summary_disclaimer(language: str = "en") -> str:
    return SUMMARY_DISCLAIMERS.get(language, SUMMARY_DISCLAIMERS["en"])


def prohibited_guidance(language: str = "en") -> str:
    return PROHIBITED_GUIDANCE_MESSAGES.get(
        language,
        PROHIBITED_GUIDANCE_MESSAGES["en"],
    )
