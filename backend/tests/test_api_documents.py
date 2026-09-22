"""End-to-end tests for the document ingestion API.

These tests run against a dedicated test database
(``settings.test_database_url``) and an in-memory storage backend.
"""

import io

from docx import Document as DocxDocument

from app.db.models import DocumentStatus


def upload(client, filename, content=b"content", content_type=None):
    return client.post(
        "/api/documents",
        files={"file": (filename, content, content_type or "application/octet-stream")},
    )


class TestUploadTxt:
    def test_upload_returns_created_document(self, db_client):
        response = upload(db_client, "notes.txt", b"Hello world.\nChunk me.")
        assert response.status_code == 201
        body = response.json()
        assert body["original_filename"] == "notes.txt"
        assert body["content_type"] == "application/octet-stream"
        assert body["file_size"] == len(b"Hello world.\nChunk me.")
        assert body["status"] == DocumentStatus.PROCESSED.value

    def test_uploaded_file_persists_chunks(self, db_client):
        response = upload(db_client, "notes.txt", b"Hello world")
        document_id = response.json()["id"]
        chunks = db_client.get(f"/api/documents/{document_id}/chunks")
        assert chunks.status_code == 200
        chunk_body = chunks.json()
        assert len(chunk_body) == 1
        assert chunk_body[0]["original_content"] == "Hello world"
        assert chunk_body[0]["metadata"]["source"] == "notes.txt"

    def test_upload_markdown(self, db_client, markdown_bytes):
        response = upload(db_client, "doc.md", markdown_bytes, "text/markdown")
        assert response.status_code == 201
        document_id = response.json()["id"]
        chunks = db_client.get(f"/api/documents/{document_id}/chunks").json()
        assert chunks[0]["original_content"] == "# Heading\n\nSome **bold** markdown text."


class TestUploadPdf:
    def test_upload_pdf_with_page_metadata(self, db_client, pdf_bytes):
        response = upload(db_client, "report.pdf", pdf_bytes, "application/pdf")
        assert response.status_code == 201
        document_id = response.json()["id"]
        chunks = db_client.get(f"/api/documents/{document_id}/chunks").json()
        assert len(chunks) == 1
        assert chunks[0]["metadata"]["page_number"] == 1
        assert "Hello PDF" in chunks[0]["original_content"]

    def test_multipage_pdf_pages_split_across_chunks(self, db_client, multi_page_pdf_bytes):
        response = upload(db_client, "book.pdf", multi_page_pdf_bytes)
        assert response.status_code == 201
        document_id = response.json()["id"]
        chunks = db_client.get(f"/api/documents/{document_id}/chunks").json()
        page_numbers = {c["metadata"]["page_number"] for c in chunks}
        assert page_numbers == {1, 2}
        indexes = [c["chunk_index"] for c in chunks]
        assert indexes == sorted(indexes)


class TestUploadDocx:
    def test_upload_docx(self, db_client):
        document = DocxDocument()
        document.add_paragraph("DOCX paragraph")
        buffer = io.BytesIO()
        document.save(buffer)
        response = upload(db_client, "letter.docx", buffer.getvalue())
        assert response.status_code == 201
        document_id = response.json()["id"]
        chunks = db_client.get(f"/api/documents/{document_id}/chunks").json()
        assert chunks[0]["original_content"] == "DOCX paragraph"
        assert "page_number" not in chunks[0]["metadata"]


class TestInvalidUploads:
    def test_rejects_unsupported_file_type(self, db_client):
        response = upload(db_client, "virus.exe", b"MZ")
        assert response.status_code == 422
        assert "Unsupported file type" in response.json()["detail"]

    def test_rejects_empty_file(self, db_client):
        response = upload(db_client, "empty.txt", b"")
        assert response.status_code == 422

    def test_rejects_empty_document_content(self, db_client):
        response = upload(db_client, "blank.txt", b"   \n   ")
        assert response.status_code == 422
        assert "no extractable text" in response.json()["detail"]

    def test_rejects_pdf_with_wrong_content(self, db_client):
        response = upload(db_client, "fake.pdf", b"this is not a pdf")
        assert response.status_code == 422
        assert "not a valid PDF" in response.json()["detail"]

    def test_pdf_with_no_text_is_rejected(self, db_client):
        response = upload(db_client, "blank.pdf", b"%PDF-1.7\n%%EOF not really but header ok...")
        assert response.status_code == 422


class TestLifecycle:
    def test_list_orders_newest_first(self, db_client):
        first = upload(db_client, "one.txt", b"first").json()["id"]
        second = upload(db_client, "two.txt", b"second").json()["id"]
        ids = [d["id"] for d in db_client.get("/api/documents").json()]
        assert ids == [second, first]

    def test_get_single_document(self, db_client):
        document_id = upload(db_client, "one.txt", b"content").json()["id"]
        response = db_client.get(f"/api/documents/{document_id}")
        assert response.status_code == 200
        assert response.json()["original_filename"] == "one.txt"

    def test_get_missing_document_returns_404(self, db_client):
        response = db_client.get("/api/documents/999999")
        assert response.status_code == 404

    def test_delete_removes_document_and_chunks(self, db_client):
        document_id = upload(db_client, "del.txt", b"to be deleted").json()["id"]
        response = db_client.delete(f"/api/documents/{document_id}")
        assert response.status_code == 204
        assert db_client.get(f"/api/documents/{document_id}").status_code == 404
        assert db_client.get(f"/api/documents/{document_id}/chunks").status_code == 404

    def test_delete_missing_document_returns_404(self, db_client):
        assert db_client.delete("/api/documents/999999").status_code == 404

    def test_chunks_of_missing_document_404(self, db_client):
        assert db_client.get("/api/documents/999999/chunks").status_code == 404