import { useState } from 'react';

const INVESTMENT_OPTIONS = [
  {
    id: 'nyse',
    name: 'NYSE - New York Stock Exchange',
    minScore: 75,
    minAmount: 50000,
    description: 'Trade US stocks - Apple, Tesla, Microsoft, Amazon',
    requirements: [
      'KYC Score ≥ 75',
      'KES 50,000+ transaction history',
      '15+ receipts over 60 days',
      'Alternative to SEC verification'
    ],
    why: 'Access the world\'s largest stock market without traditional SEC paperwork'
  },
  {
    id: 'nasdaq',
    name: 'NASDAQ - Tech Stocks',
    minScore: 75,
    minAmount: 50000,
    description: 'Invest in global tech companies - Google, Meta, Netflix',
    requirements: [
      'KYC Score ≥ 75',
      'KES 50,000+ transaction history',
      '15+ receipts over 60 days',
      'Alternative to SEC verification'
    ],
    why: 'Trade NASDAQ without US-based verification'
  },
  {
    id: 'lse',
    name: 'LSE - London Stock Exchange',
    minScore: 75,
    minAmount: 75000,
    description: 'European market access - BP, HSBC, Unilever',
    requirements: [
      'KYC Score ≥ 75',
      'KES 75,000+ transaction history',
      '15+ receipts over 60 days',
      'FCA-equivalent verification'
    ],
    why: 'Access European markets with receipt-based KYC'
  },
  {
    id: 'crypto',
    name: 'Global Crypto Exchanges',
    minScore: 70,
    minAmount: 30000,
    description: 'Trade cryptocurrency - Bitcoin, Ethereum, stablecoins',
    requirements: [
      'KYC Score ≥ 70',
      'KES 30,000+ transaction history',
      '10+ receipts over 30 days',
      'Faster than traditional crypto KYC'
    ],
    why: 'Bypass lengthy crypto exchange verification processes'
  },
  {
    id: 'forex',
    name: 'Forex Trading Platforms',
    minScore: 70,
    minAmount: 40000,
    description: 'Foreign exchange trading - USD, EUR, GBP pairs',
    requirements: [
      'KYC Score ≥ 70',
      'KES 40,000+ transaction history',
      '12+ receipts over 45 days',
      'International broker access'
    ],
    why: 'Access global forex markets with simplified verification'
  },
  {
    id: 'nse',
    name: 'NSE - Nairobi Securities Exchange',
    minScore: 65,
    minAmount: 25000,
    description: 'Local Kenyan stocks - Safaricom, KCB, Equity Bank',
    requirements: [
      'KYC Score ≥ 65',
      'KES 25,000+ transaction history',
      '8+ receipts over 30 days',
      'Simplified local verification'
    ],
    why: 'Start with local markets before going global'
  }
];

export default function InvestmentGoals({ userScore, userSpending, userReceipts }) {
  const [selectedGoal, setSelectedGoal] = useState(null);

  const getProgress = (goal) => {
    const scoreProgress = Math.min((userScore / goal.minScore) * 100, 100);
    const spendingProgress = Math.min((userSpending / goal.minAmount) * 100, 100);
    const receiptsNeeded = goal.minScore >= 75 ? 15 : goal.minScore >= 70 ? 10 : 8;
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
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Global Market Access</h2>
        <p className="text-gray-600">
          Your receipt-based verification unlocks international investment opportunities
        </p>
        <div className="mt-3 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">Why This Matters:</span> Traditional platforms like NYSE require extensive SEC verification. 
            This platform uses your everyday receipts as proof of financial activity - a faster, more accessible alternative for Kenyan investors.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
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
                  : 'border-gray-200 hover:border-gray-400'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{option.flag}</span>
                  <div>
                    <h3 className="font-bold text-gray-800 text-sm">{option.name}</h3>
                    <p className="text-xs text-gray-500">{option.description}</p>
                  </div>
                </div>
                {eligible && (
                  <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                    Eligible
                  </span>
                )}
              </div>

              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Verification Progress</span>
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
            <span className="text-5xl">{selectedGoal.flag}</span>
            <div>
              <h3 className="text-2xl font-bold">{selectedGoal.name}</h3>
              <p className="text-green-100">{selectedGoal.description}</p>
            </div>
          </div>

          <div className="bg-white/20 rounded-lg p-4 mb-4">
            <p className="text-sm font-semibold mb-2">Why Use Receipt Verification?</p>
            <p className="text-sm text-green-50">{selectedGoal.why}</p>
          </div>

          <div className="space-y-2 bg-white/10 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-sm">Verification Requirements:</h4>
            {selectedGoal.requirements.map((req, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <span className="text-green-200">•</span>
                <span>{req}</span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">Your KYC Score</p>
              <p className="text-xl font-bold">{userScore.toFixed(0)} / {selectedGoal.minScore}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).score >= 100 ? 'Complete' : `${(selectedGoal.minScore - userScore).toFixed(0)} points needed`}
              </p>
            </div>
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">Transaction History</p>
              <p className="text-xl font-bold">KES {userSpending.toFixed(0)}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).spending >= 100 ? 'Complete' : `KES ${(selectedGoal.minAmount - userSpending).toFixed(0)} needed`}
              </p>
            </div>
            <div className="bg-white/10 rounded p-3">
              <p className="text-xs text-green-100">Receipts Uploaded</p>
              <p className="text-xl font-bold">{userReceipts}</p>
              <p className="text-xs text-green-100 mt-1">
                {getProgress(selectedGoal).receipts >= 100 ? 'Complete' : 'Keep uploading'}
              </p>
            </div>
          </div>

          {isEligible(selectedGoal) && (
            <button className="w-full mt-4 bg-white text-kenya-green font-bold py-3 rounded-lg hover:bg-green-50 transition">
              Apply for {selectedGoal.name} Access →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
