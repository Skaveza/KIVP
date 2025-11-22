import { useEffect, useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { getReceipts } from '../services/api';

const COLORS = ['#006600', '#BB0000', '#FF8C00', '#4B0082', '#FFD700', '#00CED1'];

const RADIAN = Math.PI / 180;

// Custom label to avoid overlap and hide tiny slices
const renderCompanyLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  name
}) => {
  // hide labels for 0% or very small slices
  if (!percent || percent < 0.05) return null;

  const radius = outerRadius + 15;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  // shorten very long names
  const shortName = name.length > 18 ? `${name.slice(0, 18)}…` : name;
  const labelText = `${shortName}: ${(percent * 100).toFixed(0)}%`;

  return (
    <text
      x={x}
      y={y}
      fill="#006600"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={12}
    >
      {labelText}
    </text>
  );
};

export default function SpendingCharts() {
  const [companyData, setCompanyData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await getReceipts();
      const receipts = response.data.filter((r) => r.status === 'completed');

      // Spending by company
      const companySpending = {};
      receipts.forEach((receipt) => {
        const company = receipt.company_name || 'Unknown';
        const amount = parseFloat(receipt.total_amount) || 0;
        companySpending[company] = (companySpending[company] || 0) + amount;
      });

      const companyChartData = Object.entries(companySpending)
        .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(2)) }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 6);

      setCompanyData(companyChartData);

      // Monthly spending
      const monthlySpending = {};
      receipts.forEach((receipt) => {
        if (receipt.receipt_date) {
          const month = new Date(receipt.receipt_date).toLocaleDateString('en-US', {
            month: 'short'
          });
          const amount = parseFloat(receipt.total_amount) || 0;
          monthlySpending[month] = (monthlySpending[month] || 0) + amount;
        }
      });

      const monthlyChartData = Object.entries(monthlySpending).map(
        ([month, amount]) => ({ month, amount: parseFloat(amount.toFixed(2)) })
      );

      setMonthlyData(monthlyChartData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading analytics...</div>;

  return (
    <div className="space-y-6">
      {/* Spending by Company */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Spending by Company</h2>

        {companyData.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No spending data available yet</p>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={companyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={0}
                  outerRadius={100}
                  dataKey="value"
                  labelLine={false}
                  label={renderCompanyLabel}  // 🔹 custom label
                >
                  {companyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `KES ${Number(value).toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>

            <div>
              <h3 className="font-semibold text-gray-700 mb-3">Top Merchants</h3>
              <div className="space-y-2">
                {companyData.map((company, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <span className="font-medium text-gray-800">{company.name}</span>
                    </div>
                    <span className="font-bold text-kenya-green">
                      KES {company.value.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Monthly Spending Trend */}
      {monthlyData.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Spending Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `KES ${Number(value).toFixed(2)}`} />
              <Legend />
              <Bar dataKey="amount" fill="#006600" name="Spending (KES)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
