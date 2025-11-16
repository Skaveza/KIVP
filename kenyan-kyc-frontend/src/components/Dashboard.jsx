import { useState, useEffect } from 'react';
import { getDashboard, getCurrentUser } from '../services/api';
import ScoreGauge from './ScoreGauge';
import ReceiptUpload from './ReceiptUpload';
import ReceiptList from './ReceiptList';

export default function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null);
  const [score, setScore] = useState(null);
  const [stats, setStats] = useState({});
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchData = async () => {
    try {
      const [userRes, dashboardRes] = await Promise.all([
        getCurrentUser(),
        getDashboard()
      ]);
      setUser(userRes.data);
      setScore(dashboardRes.data.verification_score);
      setStats({
        total: dashboardRes.data.total_receipts,
        processed: dashboardRes.data.processed_receipts,
        pending: dashboardRes.data.pending_receipts
      });
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshKey]);

  const handleUploadSuccess = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-kenya-green text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">KYC Dashboard</h1>
          <div className="flex items-center gap-4">
            <span>{user?.full_name}</span>
            <button
              onClick={onLogout}
              className="bg-white text-kenya-green px-4 py-2 rounded hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-semibold">Total Receipts</h3>
            <p className="text-3xl font-bold text-gray-800">{stats.total || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-semibold">Processed</h3>
            <p className="text-3xl font-bold text-green-600">{stats.processed || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-semibold">Pending</h3>
            <p className="text-3xl font-bold text-yellow-600">{stats.pending || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-semibold">KYC Status</h3>
            <p className="text-xl font-bold text-gray-800">{user?.kyc_status?.toUpperCase()}</p>
          </div>
        </div>

        {/* Score and Upload */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-8 flex items-center justify-center">
            <ScoreGauge 
              score={score?.final_score || user?.kyc_score || 0} 
              status={user?.kyc_status}
            />
          </div>
          <ReceiptUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Receipt List */}
        <ReceiptList refreshTrigger={refreshKey} />
      </main>
    </div>
  );
}
