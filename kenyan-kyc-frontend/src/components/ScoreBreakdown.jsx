import { useEffect, useState } from 'react';
import { getScoreBreakdown } from '../services/api';

export default function ScoreBreakdown() {
  const [breakdown, setBreakdown] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBreakdown();
  }, []);

  const fetchBreakdown = async () => {
    try {
      const response = await getScoreBreakdown();
      setBreakdown(response.data);
    } catch (error) {
      console.error('Failed to fetch breakdown:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading breakdown...</div>;
  if (!breakdown) return <div className="text-center py-8 text-gray-500">No score data available. Upload receipts to get scored.</div>;

  const getBarColor = (score) => {
    if (score >= 75) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Score Breakdown</h2>
        <div className="text-right">
          <p className="text-3xl font-bold text-kenya-green">{breakdown.final_score}</p>
          <p className="text-sm text-gray-500">Final Score</p>
        </div>
      </div>

      <div className="space-y-6">
        {breakdown.components.map((component, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-800">{component.name}</p>
                <p className="text-xs text-gray-500">{component.description}</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-gray-700">{component.score.toFixed(0)}</p>
                <p className="text-xs text-gray-500">Weight: {(component.weight * 100).toFixed(0)}%</p>
              </div>
            </div>
            
            <div className="relative">
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(component.score)} transition-all duration-1000`}
                  style={{ width: `${component.score}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Contributes: <span className="font-semibold">{component.contribution}</span> points to final score
              </p>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-3 text-sm text-gray-700">
              💡 <span className="font-semibold">Tip:</span> {component.tip}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="font-semibold text-gray-700 mb-3">Your Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Total Receipts</p>
            <p className="text-2xl font-bold text-gray-800">{breakdown.metrics.total_receipts}</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Total Spending</p>
            <p className="text-2xl font-bold text-green-600">KES {breakdown.metrics.total_spending.toFixed(0)}</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Unique Companies</p>
            <p className="text-2xl font-bold text-blue-600">{breakdown.metrics.unique_companies}</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Unique Locations</p>
            <p className="text-2xl font-bold text-purple-600">{breakdown.metrics.unique_locations}</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Activity Period</p>
            <p className="text-2xl font-bold text-orange-600">{breakdown.metrics.date_range_days} days</p>
          </div>
        </div>
      </div>
    </div>
  );
}
