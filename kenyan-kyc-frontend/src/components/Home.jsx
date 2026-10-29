import { Receipt, ScanText, Gauge, ShieldAlert, Github } from 'lucide-react';

const steps = [
  {
    icon: <Receipt className="text-kenya-green mb-4" size={32} />,
    title: '1. Upload a receipt',
    text: 'Add a photo or PDF of a receipt (PNG, JPG or PDF, up to 5MB).',
  },
  {
    icon: <ScanText className="text-kenya-green mb-4" size={32} />,
    title: '2. We read it',
    text: 'Text recognition and a language model pull out the merchant, date and amount.',
  },
  {
    icon: <Gauge className="text-kenya-green mb-4" size={32} />,
    title: '3. You get a score',
    text: 'Receipts are combined into a score out of 100. At 75 or above, the profile counts as verified.',
  },
];

export default function Home({ onSignIn, onRegister }) {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <header className="bg-kenya-green text-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-bold">Uwezo KYC</span>
          <div className="space-x-3">
            <button onClick={onSignIn} className="px-4 py-2 rounded-lg hover:bg-green-800">
              Sign in
            </button>
            <button
              onClick={onRegister}
              className="px-4 py-2 rounded-lg bg-white text-kenya-green font-semibold hover:bg-green-50"
            >
              Create account
            </button>
          </div>
        </div>
      </header>

      <section className="bg-gradient-to-br from-kenya-green to-green-800 text-white">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <h1 className="text-4xl font-bold mb-4 max-w-2xl">
            Verifying people who have no credit history, using the receipts they already have
          </h1>
          <p className="text-lg text-green-100 max-w-2xl mb-8">
            Many people in Kenya are active buyers and savers but have no formal credit record, so
            financial services cannot verify them. Uwezo KYC tests whether everyday receipts can
            provide that evidence instead.
          </p>
          <button
            onClick={onRegister}
            className="px-6 py-3 rounded-lg bg-white text-kenya-green font-semibold hover:bg-green-50"
          >
            Try the prototype
          </button>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 py-14">
        <h2 className="text-2xl font-bold mb-8 text-center">How it works</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.title} className="bg-white rounded-xl shadow p-6">
              {step.icon}
              <h3 className="font-semibold mb-2">{step.title}</h3>
              <p className="text-gray-600">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-14">
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <ShieldAlert className="text-amber-700" size={28} />
            <h2 className="text-xl font-bold text-amber-900">Please read: this is a prototype</h2>
          </div>
          <ul className="list-disc pl-6 space-y-2 text-amber-900">
            <li>
              It is a university capstone project and must not be used for real credit or
              onboarding decisions.
            </li>
            <li>
              The model reads receipts well on a standard international test (macro F1 of 0.95) but
              less well on simulated Kenyan receipts (0.82), and it struggles most with dates
              (0.26). It has not been tested on real Kenyan receipts.
            </li>
            <li>
              The scoring weights are set by hand and have not been checked against real
              verification outcomes.
            </li>
            <li>
              Receipts and mobile money records are sensitive. Please upload sample receipts only,
              not documents containing personal or financial information you would not want
              stored.
            </li>
            <li>
              The server runs on a free plan, so the first request after a quiet period can take up
              to a minute.
            </li>
          </ul>
        </div>
      </section>

      <footer className="border-t bg-white">
        <div className="max-w-5xl mx-auto px-6 py-6 flex flex-wrap items-center justify-between gap-3 text-sm text-gray-600">
          <span>Built by Sifa Kaveza Mwachoni as a capstone project at African Leadership University.</span>
          <a
            href="https://github.com/Skaveza/KIVP"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-kenya-green font-semibold hover:underline"
          >
            <Github size={18} /> Source code
          </a>
        </div>
      </footer>
    </div>
  );
}