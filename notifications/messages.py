"""Message rendering helpers."""


def render_document_request(candidate_name: str, document_types: list[str]) -> str:
    documents = ", ".join(document_types)
    return f"{candidate_name}, please provide the following documents: {documents}"

