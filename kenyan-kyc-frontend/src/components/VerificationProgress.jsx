import { useEffect, useState } from 'react';
import { getScore, getDashboard } from '../services/api';

export default function VerificationProgress() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const [scoreRes, dashboardRes] = await Promise.all([
        getScore().catch(() => null),
        getDashboard()
      ]);

      const score = scoreRes?.data;
      const dashboard = dashboardRes.data;

      const checklistItems = [
        {
          id: 'account',
          title: 'Create Account',
          completed: true,
          color: 'green'
        },
        {
          id: 'receipts',
          title: 'Upload Receipts',
          completed: dashboard.total_receipts >= 5,
          current: dashboard.total_receipts,
          target: 10, // 10+ receipts = 30 frequency points
          description: 'Upload at least 10 receipts for good frequency score',
          color: dashboard.total_receipts >= 5 ? 'green' : 'yellow'
        },
        {
          id: 'processing',
          title: 'Process Receipts',
          completed: dashboard.processed_receipts >= 5,
          current: dashboard.processed_receipts,
          target: 10,
          description: 'Process your uploaded receipts to extract data',
          color: dashboard.processed_receipts >= 5 ? 'green' : 'yellow'
        },
        {
          id: 'spending',
          title: 'Transaction History',
          completed: score ? parseFloat(score.total_spending) >= 50000 : false,
          current: score ? parseFloat(score.total_spending) : 0,
          target: 100000, // 100,000 = max 60 spending points
          description: 'KES 50,000 for good score (45 pts), KES 100,000 for max (60 pts)',
          color: score && parseFloat(score.total_spending) >= 50000 ? 'green' : 'yellow'
        },
        {
          id: 'diversity',
          title: 'Transaction Diversity',
          completed: score ? score.unique_companies >= 3 : false,
          current: score ? score.unique_companies : 0,
          target: 5, // 5+ companies = max 60 diversity points
          description: '3+ companies for good score (45 pts), 5+ for max (60 pts)',
          color: score && score.unique_companies >= 3 ? 'green' : 'yellow'
        },
        {
          id: 'consistency',
          title: 'Consistent Activity',
          completed: score ? score.date_range_days >= 60 : false,
          current: score ? score.date_range_days : 0,
          target: 90, // 90+ days = bonus points
          description: '60+ days for bonus points, 2+ receipts/week for max consistency',
          color: score && score.date_range_days >= 60 ? 'green' : 'yellow'
        },
        {
          id: 'verification',
          title: 'Get Verified',
          completed: score ? score.is_verified : false,
          description: 'Achieve a KYC score of 75 or higher',
          color: score?.is_verified ? 'green' : 'red'
        }
      ];

      setProgress({
        items: checklistItems,
        completedCount: checklistItems.filter(item => item.completed).length,
        totalCount: checklistItems.length,
        score: score
      });

    } catch (error) {
      console.error('Failed to fetch progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading progress...</div>;
  if (!progress) return null;

  const progressPercentage = (progress.completedCount / progress.totalCount) * 100;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Verification Progress</h2>
      <p className="text-gray-600 mb-4">
        Complete these steps to get verified for investment platforms
      </p>

      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span className="font-semibold">{progress.completedCount} / {progress.totalCount} completed</span>
        </div>
        <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-kenya-green to-green-600 transition-all duration-1000"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      <div className="space-y-3">
        {progress.items.map((item) => (
          <div
            key={item.id}
            className={`border-2 rounded-lg p-4 transition ${
              item.completed
                ? 'border-green-300 bg-green-50'
                : 'border-gray-200 bg-white'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                item.completed ? 'bg-green-500' : 'bg-gray-300'
              }`}>
                {item.completed && <span className="text-white text-sm font-bold">✓</span>}
              </div>
              
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-800">{item.title}</h3>
                    {item.description && (
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                    )}
                  </div>
                  {item.completed && (
                    <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                      Complete
                    </span>
                  )}
                </div>

                {item.current !== undefined && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>
                        {item.current} / {item.target}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          item.completed ? 'bg-green-600' : 'bg-yellow-500'
                        }`}
                        style={{ width: `${Math.min((item.current / item.target) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {progress.score && !progress.score.is_verified && (
        <div className="mt-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <h4 className="font-semibold text-blue-800 mb-2">What's Next?</h4>
          <p className="text-sm text-blue-700">
            {progress.score.final_score >= 60 ? (
              <>You're close! Upload more receipts to reach the 75-point verification threshold.</>
            ) : (
              <>Continue uploading receipts regularly. Aim for at least 10 receipts from 3+ different stores over 60+ days with KES 50,000+ total spending.</>
            )}
          </p>
        </div>
      )}

      {progress.score?.is_verified && (
        <div className="mt-6 p-4 bg-green-50 border-l-4 border-green-500 rounded">
          <h4 className="font-semibold text-green-800 mb-2">Congratulations!</h4>
          <p className="text-sm text-green-700">
            You're verified! You can now access investment platforms and opportunities.
          </p>
        </div>
      )}
    </div>
  );
}