import { useState, useEffect } from 'react';

const INVESTMENT_OPTIONS = [
  {
    id: 'startup',
    name: 'Kenyan Startups',
    minScore: 70,
    minAmount: 50000,
    description: 'Invest in innovative Kenyan tech startups',
    requirements: ['KYC Score ≥ 70', 'KES 50,000+ spending history', '10+ receipts over 30 days']
  },
  {
    id: 'real-estate',
    name: 'Real Estate Projects',
    minScore: 75,
    minAmount: 100000,
    description: 'Real estate investment opportunities',
    requirements: ['KYC Score ≥ 75', 'KES 100,000+ spending history', '15+ receipts over 60 days']
  },
  {
    id: 'stocks',
    name: 'NSE Stock Market',
    minScore: 65,
    minAmount: 25000,
    description: 'Invest in Nairobi Securities Exchange',
    requirements: ['KYC Score ≥ 65', 'KES 25,000+ spending history', '8+ receipts over 30 days']
  },
  {
    id: 'bonds',
    name: 'Government Bonds',
    minScore: 80,
    minAmount: 150000,
    description: 'Safe government treasury bonds',
    requirements: ['KYC Score ≥ 80', 'KES 150,000+ spending history', '20+ receipts over 90 days']
  }
];

export default function InvestmentGoals({ userScore, userSpending, userReceipts }) {
  const [selectedGoal, setSelectedGoal] = useState(null);

  const getProgress = (goal) => {
    const scoreProgress = Math.min((userScore / goal.minScore) * 100, 100);
    const spendingProgress = Math.min((userSpending / goal.minAmount) * 100, 100);
    const receiptsNeeded = goal.minScore >= 80 ? 20 : goal.minScore >= 75 ? 15 : goal.minScore >= 70 ? 10 : 8;
    const receiptProgress = Math.min((userReceipts / receiptsNeeded) * 100, 100);
    
    return {
      overall: (scoreProgress + spendingProgress + receiptProgress) / 3,
      score: scoreProgress,
      spending: spendingProgress,
      receipts: receiptProgress
    };
  };

  const isEligible = (goal) => {
    const progress = getProgress(goal);
    return progress.overall >= 100;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Investment Goals</h2>
      <p className="text-gray-600 mb-6">Select your investment target and track your progress</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {INVESTMENT_OPTIONS.map((option) => {
          const progress = getProgress(option);
          const eligible = isEligible(option);
          
          return (
            <div
              key={option.id}
              onClick={() => setSelectedGoal(option)}
              className={`border-2 rounded-lg p-4 cursor-pointer transition ${
                selectedGoal?.id === option.id
                  ? 'border-kenya-green bg-green-50'
                  : eligible
                  ? 'border-green-300 hover:border-green-500'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-3xl">{option.icon}</span>
                  <div>
                    <h3 className="font-bold text-gray-800">{option.name}</h3>
                    <p className="text-xs text-gray-500">{option.description}</p>
                  </div>
                </div>
                {eligible && (
                  <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                    ✓ Eligible
                  </span>
                )}
              </div>

              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Progress</span>
                  <span className="font-semibold">{progress.overall.toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      eligible ? 'bg-green-600' : 'bg-blue-500'
                    }`}
                    style={{ width: `${progress.overall}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedGoal && (
        <div className="bg-gradient-to-r from-kenya-green to-green-700 text-white rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">{selectedGoal.icon}</span>
            <div>
              <h3 className="text-2xl font-bold">{selectedGoal.name}</h3>
              <p className="text-green-100">{selectedGoal.description}</p>
            </div>
          </div>

          <div className="space-y-3 bg-white/10 rounded-lg p-4">
            <h4 className="font-semibold text-sm">Requirements:</h4>
            {selectedGoal.requirements.map((req, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <span>✓</span>
                <span>{req}</span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">KYC Score</p>
              <p className="text-xl font-bold">{userScore.toFixed(0)} / {selectedGoal.minScore}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).score >= 100 ? '✓ Complete' : `${(100 - getProgress(selectedGoal).score).toFixed(0)}% to go`}
              </p>
            </div>
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">Spending</p>
              <p className="text-xl font-bold">KES {userSpending.toFixed(0)}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).spending >= 100 ? '✓ Complete' : `${(100 - getProgress(selectedGoal).spending).toFixed(0)}% to go`}
              </p>
            </div>
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">Receipts</p>
              <p className="text-xl font-bold">{userReceipts}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).receipts >= 100 ? '✓ Complete' : `${(100 - getProgress(selectedGoal).receipts).toFixed(0)}% to go`}
              </p>
            </div>
          </div>

          {isEligible(selectedGoal) && (
            <button className="w-full mt-4 bg-white text-kenya-green font-bold py-3 rounded-lg hover:bg-green-50 transition">
              Apply for {selectedGoal.name} →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
