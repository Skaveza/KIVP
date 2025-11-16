import { useState, useEffect } from 'react';
import { getReceipts, processReceipt, deleteReceipt } from '../services/api';

export default function ReceiptList({ refreshTrigger }) {
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

  const handleProcess = async (id) => {
    try {
      await processReceipt(id);
      alert('Receipt processed!');
      fetchReceipts();
    } catch (error) {
      alert('Processing failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this receipt?')) return;
    try {
      await deleteReceipt(id);
      fetchReceipts();
    } catch (error) {
      alert('Delete failed');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colors[status] || colors.pending}`}>
        {status}
      </span>
    );
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Receipts</h2>
      
      {receipts.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No receipts uploaded yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {receipts.map((receipt) => (
                <tr key={receipt.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm">{receipt.file_name}</td>
                  <td className="px-4 py-3">{getStatusBadge(receipt.status)}</td>
                  <td className="px-4 py-3 text-sm">{receipt.company_name || '-'}</td>
                  <td className="px-4 py-3 text-sm">
                    {receipt.total_amount ? `KES ${receipt.total_amount}` : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm">{receipt.receipt_date || '-'}</td>
                  <td className="px-4 py-3 text-sm">
                    {receipt.status === 'pending' && (
                      <button
                        onClick={() => handleProcess(receipt.id)}
                        className="text-blue-600 hover:underline mr-2"
                      >
                        Process
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(receipt.id)}
                      className="text-red-600 hover:underline"
                    >
                      Delete
                    </button>
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
