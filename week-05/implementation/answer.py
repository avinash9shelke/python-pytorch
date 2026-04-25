from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages
from langchain_core.documents import Document
from chromadb.errors import InvalidArgumentError, NotFoundError

from dotenv import load_dotenv


load_dotenv(override=True)

MODEL = "gpt-4.1-nano"
DB_NAME = str(Path(__file__).parent.parent / "vector_db")
COLLECTION_NAME = "netflix_knowledge_base"

# Keep dimensions aligned with the existing persisted Chroma collection.
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=384)
RETRIEVAL_K = 10

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the Netflix LLM.
You are chatting with a user about Netflix LLM.
If relevant, use the given context to answer any question.
If you don't know the answer, say so.
Context:
{context}
"""

llm = ChatOpenAI(temperature=0, model_name=MODEL)
_retriever = None


def _build_retriever():
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_NAME,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever()


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = _build_retriever()
    return _retriever


def fetch_context(question: str) -> list[Document]:
    """
    Retrieve relevant context documents for a question.
    """
    try:
        return _get_retriever().invoke(question, k=RETRIEVAL_K)
    except NotFoundError as exc:
        # Retry once with a fresh client/retriever to recover from stale collection handles.
        global _retriever
        _retriever = _build_retriever()
        try:
            return _retriever.invoke(question, k=RETRIEVAL_K)
        except NotFoundError as retry_exc:
            raise RuntimeError(
                "Chroma collection was not found in the persisted DB. "
                "Run `uv run week-05/implementation/ingest.py` to rebuild vectors."
            ) from retry_exc
    except InvalidArgumentError as exc:
        raise RuntimeError(
            "Embedding dimension mismatch between retriever and Chroma DB. "
            "Run `uv run week-05/implementation/ingest.py` to rebuild vectors with "
            "the configured embedding model."
        ) from exc


def combined_question(question: str, history: list[dict] = []) -> str:
    """
    Combine all the user's messages into a single string.
    """
    prior = "\n".join(m["content"] for m in history if m["role"] == "user")
    return prior + "\n" + question


def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document]]:
    """
    Answer the given question with RAG; return the answer and the context documents.
    """
    combined = combined_question(question, history)
    docs = fetch_context(combined)
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content, docs