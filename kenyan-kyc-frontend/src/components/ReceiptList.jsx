// src/components/ReceiptList.jsx
import { useState, useEffect } from 'react';
import { getReceipts, deleteReceipt, getReceiptFile } from '../services/api';


export default function ReceiptList({ refreshTrigger, onReceiptsChanged }) {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReceipts = async () => {
    try {
      const response = await getReceipts();
      setReceipts(response.data);
    } catch (error) {
      console.error('Failed to fetch receipts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReceipts();
  }, [refreshTrigger]);

  const handleView = async (id) => {
    try {
      const res = await getReceiptFile(id);
  
      const contentType =
        res.headers?.['content-type'] || 'application/octet-stream';
  
      const blob = new Blob([res.data], { type: contentType });
      const fileURL = URL.createObjectURL(blob);
  
      window.open(fileURL, '_blank', 'noopener,noreferrer');
  
      // cleanup to avoid memory leaks
      setTimeout(() => URL.revokeObjectURL(fileURL), 60_000);
    } catch (error) {
      console.error('View failed:', error);
      alert(
        'View failed: ' +
          (error.response?.data?.detail || error.message)
      );
    }
  };
  const handleDelete = async (id) => {
    if (!confirm('Delete this receipt? This may also update your KYC score.')) return;
    try {
      await deleteReceipt(id);
      await fetchReceipts();
      //  Tell parent (Dashboard) to refresh stats + score
      if (onReceiptsChanged) {
        onReceiptsChanged();
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Delete failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-semibold ${
          colors[status] || colors.pending
        }`}
      >
        {status}
      </span>
    );
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div className="bg-white rounded-lg  p-6">

      {receipts.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No receipts uploaded yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  File
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Company
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {receipts.map((receipt) => (
                <tr key={receipt.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm">{receipt.file_name}</td>
                  <td className="px-4 py-3">{getStatusBadge(receipt.status)}</td>
                  <td className="px-4 py-3 text-sm">{receipt.company_name || '-'}</td>
                  <td className="px-4 py-3 text-sm">
                    {receipt.total_amount != null
                      ? `${receipt.currency || 'KES'} ${receipt.total_amount}`
                      : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {receipt.receipt_date
                      ? new Date(receipt.receipt_date).toLocaleDateString()
                      : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm space-x-3">
                    <button
                      onClick={() => handleView(receipt.id)}
                      className="text-kenya-green font-semibold hover:underline"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(receipt.id)}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                    {/* No manual "Process" button since uploads auto-process */}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
