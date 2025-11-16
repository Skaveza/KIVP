import { useState } from 'react';
import { uploadReceipt, processReceipt } from '../services/api';

export default function BatchUpload({ onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadedReceipts, setUploadedReceipts] = useState([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleBatchUpload = async () => {
    setUploading(true);
    setProgress({ current: 0, total: files.length });
    const receipts = [];

    for (let i = 0; i < files.length; i++) {
      try {
        const response = await uploadReceipt(files[i]);
        receipts.push(response.data);
        setProgress({ current: i + 1, total: files.length });
      } catch (error) {
        console.error(`Failed to upload ${files[i].name}:`, error);
      }
    }

    setUploadedReceipts(receipts);
    setFiles([]);
    setUploading(false);
  };

  const handleProcessAll = async () => {
    setProcessing(true);
    setProgress({ current: 0, total: uploadedReceipts.length });

    for (let i = 0; i < uploadedReceipts.length; i++) {
      try {
        await processReceipt(uploadedReceipts[i].id);
        setProgress({ current: i + 1, total: uploadedReceipts.length });
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`Failed to process receipt:`, error);
      }
    }

    setProcessing(false);
    setUploadedReceipts([]);
    if (onUploadComplete) onUploadComplete();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Batch Upload Receipts</h2>
      
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
          <svg className="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-gray-600 font-semibold">Click to select multiple files</p>
          <p className="text-xs text-gray-500 mt-1">or drag and drop (PNG, JPG, PDF)</p>
        </label>
      </div>

      {files.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-gray-700 mb-2">Selected Files ({files.length})</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                <span className="text-sm text-gray-700 truncate flex-1">{file.name}</span>
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
            {uploading ? `Uploading ${progress.current}/${progress.total}...` : `Upload All ${files.length} Files`}
          </button>
        </div>
      )}

      {uploadedReceipts.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 mb-2">
            ✓ {uploadedReceipts.length} files uploaded successfully!
          </h3>
          <button
            onClick={handleProcessAll}
            disabled={processing}
            className="w-full bg-kenya-green text-white py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {processing ? `Processing ${progress.current}/${progress.total}...` : 'Process All Receipts'}
          </button>
        </div>
      )}
    </div>
  );
}
