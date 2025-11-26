import { useState, useEffect } from 'react';
import { getDashboard, getCurrentUser } from '../services/api';
import ScoreGauge from './ScoreGauge';
import ReceiptUpload from './ReceiptUpload';
import ReceiptList from './ReceiptList';
import ScoreBreakdown from './ScoreBreakdown';
import InvestmentGoals from './InvestmentGoals';
import SpendingCharts from './SpendingCharts';
import VerificationProgress from './VerificationProgress';
import BatchUpload from './BatchUpload';

export default function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null);
  const [score, setScore] = useState(null);
  const [stats, setStats] = useState({});
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeTab, setActiveTab] = useState('overview');

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

  const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'upload', name: 'Upload Receipts' },
    { id: 'receipts', name: 'My Receipts' },
    { id: 'score', name: 'Score Details' },
    { id: 'analytics', name: 'Analytics' },
    { id: 'investments', name: 'Investment Goals' },
    { id: 'progress', name: 'Verification' }
  ];

  return (
    <div className="min-h-screen bg-gray-100 ">
      {/* Header with Kenyan Flag Colors */}
      <header className="bg-gradient-to-r from-kenya-green via-kenya-black to-kenya-red text-white shadow-lg fixed w-full z-[2]">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Uwezo KYC</h1>
              <p className="text-sm text-green-100">Receipt-Based Verification • Global Market Access</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-semibold">{user?.full_name}</p>
                <p className="text-xs text-green-100">{user?.email}</p>
              </div>
              <button
                onClick={onLogout}
                className="bg-white text-kenya-green px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 mt-20">
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-kenya-green">
            <h3 className="text-gray-500 text-sm font-semibold">Total Receipts</h3>
            <p className="text-3xl font-bold text-gray-800">{stats.total || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Uploaded receipts</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
            <h3 className="text-gray-500 text-sm font-semibold">Processed</h3>
            <p className="text-3xl font-bold text-green-600">{stats.processed || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Data extracted</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-yellow-500">
            <h3 className="text-gray-500 text-sm font-semibold">Pending</h3>
            <p className="text-3xl font-bold text-yellow-600">{stats.pending || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Awaiting processing</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-kenya-red">
            <h3 className="text-gray-500 text-sm font-semibold">KYC Status</h3>
            <p className="text-xl font-bold text-gray-800">
              {user?.kyc_status?.toUpperCase() || 'PENDING'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Verification status</p>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white rounded-lg shadow-lg mb-8 overflow-hidden">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 min-w-fit px-6 py-4 font-semibold transition ${
                  activeTab === tab.id
                    ? 'bg-kenya-green text-white border-b-4 border-kenya-black'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* KYC Score Gauge */}
                <div className="bg-white rounded-lg shadow-lg p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Your KYC Score</h2>
                  <div className="flex items-center justify-center">
                    <ScoreGauge 
                      score={score?.final_score || user?.kyc_score || 0} 
                      status={user?.kyc_status}
                    />
                  </div>
                  <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Tip:</span> Upload your everyday transaction receipts to build your verification score and establish your financial history.
                    </p>
                  </div>
                </div>

                {/* Quick Upload */}
                <ReceiptUpload onUploadSuccess={handleUploadSuccess} />
              </div>

              {/* Recent Activity Preview */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-800">Recent Receipts</h2>
                  <button
                    onClick={() => setActiveTab('receipts')}
                    className="text-kenya-green font-semibold hover:underline"
                  >
                    View All →
                  </button>
                </div>
                <ReceiptList refreshTrigger={refreshKey}  onReceiptsChanged={handleUploadSuccess}/>
              </div>
            </>
          )}

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <ReceiptUpload onUploadSuccess={handleUploadSuccess} />
              <BatchUpload onUploadComplete={handleUploadSuccess} />
            </div>
          )}

          {/* Receipts Tab */}
          {activeTab === 'receipts' && (
            <ReceiptList refreshTrigger={refreshKey} onReceiptsChanged={handleUploadSuccess} />
          )}

          {/* Score Details Tab */}
          {activeTab === 'score' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-lg p-8 sticky top-8">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">Your Score</h3>
                  <ScoreGauge 
                    score={score?.final_score || user?.kyc_score || 0} 
                    status={user?.kyc_status}
                  />
                </div>
              </div>
              <div className="lg:col-span-2">
                <ScoreBreakdown />
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <SpendingCharts />
          )}

          {/* Investment Goals Tab */}
          {activeTab === 'investments' && (
            <InvestmentGoals 
              userScore={score?.final_score || user?.kyc_score || 0}
              userSpending={score?.total_spending || 0}
              userReceipts={stats.processed || 0}
            />
          )}

          {/* Verification Progress Tab */}
          {activeTab === 'progress' && (
            <VerificationProgress />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-kenya-black text-white mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm">Kenyan KYC Verification Platform • Receipt-Based Investor Authentication</p>
          <p className="text-xs text-gray-400 mt-2">
            Thesis Demonstration • {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}