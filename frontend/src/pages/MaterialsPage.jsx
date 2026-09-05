import React, { useEffect, useState } from "react";
import { FileText, Search, UploadCloud } from "lucide-react";

import { getDocuments, retryDocument, uploadDocument } from "../services/api";

export default function MaterialsPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [subject, setSubject] = useState("General");
  const [description, setDescription] = useState("");
  const [documents, setDocuments] = useState([]);
  const [status, setStatus] = useState("");

  async function refreshDocuments() {
    const data = await getDocuments();
    setDocuments(data);
  }

  useEffect(() => {
    refreshDocuments().catch(() => setDocuments([]));
  }, []);

  async function handleUpload() {
    if (!selectedFile) return;
    setStatus("Uploading and processing...");
    try {
      await uploadDocument({ file: selectedFile, subject, description });
      await refreshDocuments();
      setSelectedFile(null);
      setDescription("");
      setStatus("Upload started. Refresh in a moment to see processing status.");
    } catch (error) {
      setStatus(error.response?.data?.detail ?? "Upload failed. Check backend configuration.");
    }
  }

  async function handleRetry(documentId) {
    setStatus("Retrying document processing...");
    try {
      await retryDocument(documentId);
      await refreshDocuments();
      setStatus("Retry started. Refresh in a moment to see the latest status.");
    } catch (error) {
      setStatus(error.response?.data?.detail ?? "Retry failed. Check backend configuration.");
    }
  }

  return (
    <div className="workspace-page">
      <section className="page-header">
        <div>
          <p className="eyebrow">Document pipeline</p>
          <h1>Study Materials</h1>
          <p>Upload PDFs, track processing status, and prepare content for chunking, embeddings, and retrieval.</p>
        </div>
      </section>

      <section className="materials-grid">
        <form className="upload-panel">
          <UploadCloud size={34} />
          <h2>Upload PDF</h2>
          <p>PDF validation, extraction, chunking, and vector storage will connect here in the document phase.</p>
          <label className="file-picker">
            <input
              type="file"
              accept="application/pdf"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
            Choose PDF
          </label>
          <input value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="Subject" />
          <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" />
          {selectedFile && <strong className="selected-file">{selectedFile.name}</strong>}
          <button className="primary-action" type="button" disabled={!selectedFile} onClick={handleUpload}>
            <UploadCloud size={18} />
            Upload
          </button>
          {status && <p className="form-status">{status}</p>}
        </form>

        <div className="materials-panel">
          <div className="search-box">
            <Search size={18} />
            <input placeholder="Search filename, subject, topic, or content" />
          </div>

          {documents.length === 0 ? (
            <div className="empty-state">
              <FileText size={42} />
              <h2>No materials uploaded yet</h2>
              <p>Your documents will appear here with subject, upload date, and processing status.</p>
            </div>
          ) : (
            <div className="document-list">
              {documents.map((doc) => (
                <article className="document-row" key={doc.id}>
                  <FileText size={20} />
                  <div>
                    <strong>{doc.original_filename}</strong>
                    <span>{doc.subject}</span>
                    {doc.processing_error && <small>{doc.processing_error}</small>}
                  </div>
                  <div className="document-actions">
                    <mark className={`status-badge ${doc.processing_status}`}>{doc.processing_status}</mark>
                    {doc.processing_status === "failed" && (
                      <button className="secondary-action" type="button" onClick={() => handleRetry(doc.id)}>
                        Retry
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
