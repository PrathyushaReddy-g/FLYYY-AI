import re
from typing import List, Dict, Any, Optional
from app.schemas import DiscoveryField

try:
    from presidio_analyzer import AnalyzerEngine
    presidio_analyzer = AnalyzerEngine()
except Exception:
    presidio_analyzer = None

class DiscoveryService:
    """
    Dynamic PII Discovery Service using Microsoft Presidio and pattern heuristics.
    Computes genuine confidence scores and recommended protection policies.
    """

    # Heuristic regex patterns for fallback or fast verification
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,15}$")
    NUMERIC_10_REGEX = re.compile(r"^[0-9]{10}$")

    def mask_value(self, val: str, classification: str) -> str:
        """Create safe masked presentation string for UI."""
        s = str(val).strip()
        if not s:
            return ""
        if classification == "EMAIL" and "@" in s:
            parts = s.split("@", 1)
            name_part = parts[0]
            domain_part = parts[1]
            masked_name = name_part[0] + "*" * (len(name_part) - 1) if len(name_part) > 1 else "*"
            return f"{masked_name}@{domain_part}"
        elif classification == "PHONE":
            digits = [c for c in s if c.isdigit()]
            if len(digits) >= 4:
                return "*" * (len(digits) - 4) + "".join(digits[-4:])
            return "*" * len(s)
        elif classification == "PERSON":
            words = s.split()
            masked_words = []
            for w in words:
                if len(w) > 2:
                    masked_words.append(w[0] + "*" * (len(w) - 2) + w[-1])
                elif len(w) > 0:
                    masked_words.append(w[0] + "*")
            return " ".join(masked_words)
        return s[:2] + "*" * max(0, len(s) - 4) + s[-2:] if len(s) > 4 else "***"

    def discover_column(self, field_name: str, sample_values: List[Any], col_type: str = "string") -> DiscoveryField:
        """
        Analyze a column's name and sample values dynamically.
        Never returns unmasked PII.
        """
        clean_samples = [str(v).strip() for v in sample_values if v is not None and str(v).strip()]
        field_lower = field_name.lower()

        classification = "GENERIC"
        confidence = 0.50
        recommended = "KEEP"

        # 1. Inspect field name heuristics
        name_signal = None
        if any(term in field_lower for term in ["email", "mail", "e_mail"]):
            name_signal = "EMAIL"
        elif any(term in field_lower for term in ["mobile", "phone", "cell", "contact_no"]):
            name_signal = "PHONE"
        elif any(term in field_lower for term in ["name", "full_name", "first_name", "last_name", "customer_name"]):
            name_signal = "PERSON"
        elif any(term in field_lower for term in ["customer_id", "user_id", "ssn", "national_id"]):
            name_signal = "IDENTIFIER"
        elif any(term in field_lower for term in ["city", "country", "state", "region", "zip", "postal"]):
            name_signal = "LOCATION"

        # 2. Inspect sample values
        email_matches = 0
        phone_matches = 0
        numeric_10_matches = 0
        presidio_person_scores = []
        presidio_email_scores = []
        presidio_phone_scores = []

        for sample in clean_samples[:10]:
            if self.EMAIL_REGEX.match(sample):
                email_matches += 1
            if self.PHONE_REGEX.match(sample):
                phone_matches += 1
            if self.NUMERIC_10_REGEX.match("".join(c for c in sample if c.isdigit())):
                numeric_10_matches += 1

            if presidio_analyzer:
                try:
                    results = presidio_analyzer.analyze(text=sample, language="en")
                    for r in results:
                        if r.entity_type == "PERSON":
                            presidio_person_scores.append(r.score)
                        elif r.entity_type == "EMAIL_ADDRESS":
                            presidio_email_scores.append(r.score)
                        elif r.entity_type == "PHONE_NUMBER":
                            presidio_phone_scores.append(r.score)
                except Exception:
                    pass

        sample_count = max(1, len(clean_samples[:10]))
        email_ratio = email_matches / sample_count
        phone_ratio = phone_matches / sample_count

        # Compute dynamic classification and confidence
        if email_ratio >= 0.5 or (name_signal == "EMAIL" and email_ratio > 0):
            classification = "EMAIL"
            confidence = round(min(0.99, 0.85 + 0.14 * email_ratio), 2)
            recommended = "TOKENIZE"
        elif phone_ratio >= 0.5 or (name_signal == "PHONE" and phone_ratio > 0):
            classification = "PHONE"
            confidence = round(min(0.99, 0.85 + 0.14 * phone_ratio), 2)
            recommended = "FPE"
        elif name_signal == "PERSON":
            classification = "PERSON"
            avg_presidio = (sum(presidio_person_scores) / len(presidio_person_scores)) if presidio_person_scores else 0.88
            confidence = round(min(0.98, max(0.88, avg_presidio)), 2)
            recommended = "TOKENIZE"
        elif name_signal == "IDENTIFIER":
            classification = "IDENTIFIER"
            confidence = 0.95
            recommended = "KEEP"  # Primary business ID retained for downstream joins
        elif name_signal == "LOCATION":
            classification = "LOCATION"
            confidence = 0.85
            recommended = "KEEP"
        else:
            classification = "GENERIC"
            confidence = 0.60
            recommended = "KEEP"

        sample_masked = self.mask_value(clean_samples[0], classification) if clean_samples else None

        return DiscoveryField(
            field_name=field_name,
            data_type=col_type,
            classification=classification,
            confidence=confidence,
            recommended_protection=recommended,
            sample_masked=sample_masked
        )

    def discover_dataframe_or_dict(self, records: List[Dict[str, Any]]) -> List[DiscoveryField]:
        if not records:
            return []
        keys = list(records[0].keys())
        fields = []
        for k in keys:
            samples = [r.get(k) for r in records[:20]]
            # Infer basic type
            col_type = "string"
            if all(isinstance(s, int) for s in samples if s is not None):
                col_type = "integer"
            elif all(isinstance(s, float) for s in samples if s is not None):
                col_type = "float"
            fields.append(self.discover_column(k, samples, col_type))
        return fields


discovery_service = DiscoveryService()
