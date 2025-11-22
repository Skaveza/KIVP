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
  if (!breakdown)
    return (
      <div className="text-center py-8 text-gray-500">
        No score data available. Upload receipts to get scored.
      </div>
    );

  const getBarColor = (score) => {
    if (score >= 75) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const receiptsUsed = breakdown.receipts_used || [];
  const receiptsDropped = breakdown.receipts_dropped || [];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-8">
      {/* Header + main breakdown */}
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-gray-800">Score Breakdown</h2>
        <div className="text-right">
          <p className="text-3xl font-bold text-kenya-green">
            {Number(breakdown.final_score || 0).toFixed(0)}
          </p>
          <p className="text-sm text-gray-500">Final Score</p>
        </div>
      </div>

      {/* Components */}
      <div className="space-y-6">
        {breakdown.components.map((component, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-800">{component.name}</p>
                <p className="text-xs text-gray-500">{component.description}</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-gray-700">
                  {Number(component.score || 0).toFixed(0)}
                </p>
                <p className="text-xs text-gray-500">
                  Weight: {(component.weight * 100).toFixed(0)}%
                </p>
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
                Contributes:{' '}
                <span className="font-semibold">
                  {Number(component.contribution || 0).toFixed(2)}
                </span>{' '}
                points to final score
              </p>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-3 text-sm text-gray-700">
              💡 <span className="font-semibold">Tip:</span> {component.tip}
            </div>
          </div>
        ))}
      </div>

      {/* Metrics */}
      <div className="pt-6 border-t border-gray-200">
        <h3 className="font-semibold text-gray-700 mb-3">Your Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Total Receipts (used)</p>
            <p className="text-2xl font-bold text-gray-800">
              {breakdown.metrics.total_receipts}
            </p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Total Spending (used)</p>
            <p className="text-2xl font-bold text-green-600">
              KES {Number(breakdown.metrics.total_spending || 0).toFixed(0)}
            </p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Unique Companies</p>
            <p className="text-2xl font-bold text-blue-600">
              {breakdown.metrics.unique_companies}
            </p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Unique Locations</p>
            <p className="text-2xl font-bold text-purple-600">
              {breakdown.metrics.unique_locations}
            </p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-xs text-gray-500">Activity Period</p>
            <p className="text-2xl font-bold text-orange-600">
              {breakdown.metrics.date_range_days} days
            </p>
          </div>
        </div>
      </div>

      {/* Receipts used vs dropped */}
      {(receiptsUsed.length > 0 || receiptsDropped.length > 0) && (
        <div className="pt-6 border-t border-gray-200 space-y-4">
          <h3 className="font-semibold text-gray-700">
            How your receipts were evaluated
          </h3>

          {/* Used */}
          {receiptsUsed.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-green-700 mb-2">
                 Receipts included in your KYC score
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        File
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Company
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Amount
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Date
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {receiptsUsed.map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50">
                        <td className="px-3 py-2">{r.file_name}</td>
                        <td className="px-3 py-2">
                          {r.company_name || <span className="text-gray-400">–</span>}
                        </td>
                        <td className="px-3 py-2">
                          {r.total_amount != null
                            ? `KES ${r.total_amount.toFixed(2)}`
                            : '–'}
                        </td>
                        <td className="px-3 py-2">
                          {r.receipt_date || <span className="text-gray-400">–</span>}
                        </td>
                        <td className="px-3 py-2">
                          {(r.overall_confidence * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Dropped */}
          {receiptsDropped.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-red-700 mb-2">
                ⚠️ Receipts ignored by the KYC score
              </h4>
              <p className="text-xs text-gray-500 mb-2">
                These files were uploaded but not trusted enough to influence your
                score (e.g. low confidence or suspicious amount).
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        File
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Amount
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Confidence
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Reason
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {receiptsDropped.map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50">
                        <td className="px-3 py-2">{r.file_name}</td>
                        <td className="px-3 py-2">
                          {r.total_amount != null
                            ? `KES ${r.total_amount.toFixed(2)}`
                            : '–'}
                        </td>
                        <td className="px-3 py-2">
                          {(r.overall_confidence * 100).toFixed(1)}%
                        </td>
                        <td className="px-3 py-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            {r.reason_if_dropped}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
