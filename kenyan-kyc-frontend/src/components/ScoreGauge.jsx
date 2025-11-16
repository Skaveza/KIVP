export default function ScoreGauge({ score, status }) {
  const percentage = score || 0;
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const getColor = () => {
    if (percentage >= 75) return '#006600';
    if (percentage >= 60) return '#FF8C00';
    return '#BB0000';
  };

  const getStatusText = () => {
    if (percentage >= 75) return 'VERIFIED';
    if (percentage >= 60) return 'UNDER REVIEW';
    return 'PENDING';
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width="200" height="200" className="transform -rotate-90">
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke="#e5e7eb"
            strokeWidth="12"
            fill="none"
          />
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke={getColor()}
            strokeWidth="12"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color: getColor() }}>
            {percentage.toFixed(0)}
          </span>
          <span className="text-gray-500 text-sm">/ 100</span>
        </div>
      </div>
      <div className="mt-4 text-center">
        <p className="text-2xl font-bold" style={{ color: getColor() }}>
          {status || getStatusText()}
        </p>
        <p className="text-gray-500 text-sm mt-1">KYC Status</p>
      </div>
    </div>
  );
}
