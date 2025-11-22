// src/components/BatchUpload.jsx
import { useState } from 'react';
import { uploadReceipt } from '../services/api';

export default function BatchUpload({ onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...selectedFiles]);
    setResults([]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleBatchUpload = async () => {
    if (!files.length) {
      alert('Please select at least one file.');
      return;
    }

    setUploading(true);
    setProgress({ current: 0, total: files.length });
    const newResults = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        const response = await uploadReceipt(file);
        newResults.push({
          fileName: file.name,
          status: 'success',
          message: `Uploaded and processed (KYC updated).`,
          serverId: response.data.id,
        });
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        newResults.push({
          fileName: file.name,
          status: 'error',
          message:
            error.response?.data?.detail ||
            error.message ||
            'Upload failed',
        });
      }
      setProgress({ current: i + 1, total: files.length });
    }

    setResults(newResults);
    setFiles([]);
    setUploading(false);

    // Refresh dashboard cards + score + receipts
    if (onUploadComplete) {
      onUploadComplete();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Batch Upload Receipts
      </h2>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 mb-4">
        <input
          type="file"
          multiple
          accept="image/*,.pdf"
          onChange={handleFileSelect}
          className="hidden"
          id="batch-upload"
        />
        <label
          htmlFor="batch-upload"
          className="flex flex-col items-center cursor-pointer"
        >
          <svg
            className="w-12 h-12 text-gray-400 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-gray-600 font-semibold">
            Click to select multiple files
          </p>
          <p className="text-xs text-gray-500 mt-1">
            or drag and drop (PNG, JPG, PDF)
          </p>
        </label>
      </div>

      {/* Selected files list */}
      {files.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 mb-2">
            Selected Files ({files.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-gray-50 p-2 rounded"
              >
                <span className="text-sm text-gray-700 truncate flex-1">
                  {file.name}
                </span>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700 ml-2"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={handleBatchUpload}
            disabled={uploading}
            className="w-full mt-3 bg-kenya-green text-white py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {uploading
              ? `Uploading ${progress.current}/${progress.total}...`
              : `Upload All ${files.length} Files`}
          </button>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 mb-2">
            Upload summary
          </h3>
          <ul className="space-y-1 text-sm">
            {results.map((r, idx) => (
              <li key={idx}>
                <span className="font-medium">{r.fileName}:</span>{' '}
                <span
                  className={
                    r.status === 'success'
                      ? 'text-green-700'
                      : 'text-red-600'
                  }
                >
                  {r.message}
                </span>
              </li>
            ))}
          </ul>
          <p className="text-xs text-gray-600 mt-2">
            Your dashboard, score details, and receipts list should now
            reflect these uploads.
          </p>
        </div>
      )}
    </div>
  );
}
