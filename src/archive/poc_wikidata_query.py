import re
import sys
from qwikidata.entity import WikidataItem
from qwikidata.linked_data_interface import get_entity_dict_from_api

QCODE_PATTERN: str = "^Q[1-9][0-9]*$"
QCODE_REGEX = re.compile(QCODE_PATTERN)
MULTIPLE_QCODES_PATTERN: str = "^Q[1-9][0-9]*(;\\s*Q[1-9][0-9]*)*"
MULTIPLE_QCODES_REGEX = re.compile(MULTIPLE_QCODES_PATTERN)


def get_qids(qcodes) -> list:
    if (
        not isinstance(qcodes, str)
        and isinstance(qcodes, list)
        and not all(isinstance(item, str) for item in qcodes)
    ):
        return []

    if isinstance(qcodes, list):
        return all(MULTIPLE_QCODES_REGEX.search(qcode) for qcode in qcodes)


def fetch_wikidata_entity(qcode):
    """
    Fetches a Wikidata entity's label and description for a given Q-code.

    Args:
        qcode (str): The Wikidata Q-code (e.g., 'Q42').

    Returns:
        dict: A dictionary with 'id', 'label', and 'description'.
    """
    # Basic validation
    if (
        not isinstance(qcode, str)
        or not qcode.startswith("Q")
        or not qcode[1:].isdigit()
    ):
        raise ValueError(f"Invalid Q-code format: {qcode}")

    try:
        entity_dict = get_entity_dict_from_api(qcode)
        entity = WikidataItem(entity_dict)

        label = entity.get_label("en") or "No label found"
        description = entity.get_description("en") or "No description found"

        return {"id": qcode, "label": label, "description": description}
    except Exception as e:
        raise RuntimeError(f"Error fetching {qcode}: {e}")


if __name__ == "__main__":
    # Example Q-codes
    qcodes = ["Q42", "Q1", "Q90"]  # Douglas Adams, Universe, Paris

    for code in qcodes:
        try:
            data = fetch_wikidata_entity(code)
            print(f"{data['id']}: {data['label']} — {data['description']}")
        except Exception as err:
            print(f"Failed to fetch {code}: {err}", file=sys.stderr)
