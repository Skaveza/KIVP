import {
  Upload,
  ScanText,
  Filter,
  Gauge,
  ShieldCheck,
  Lock,
  FlaskConical,
  ArrowRight,
  Github,
} from 'lucide-react';

const GITHUB_URL = 'https://github.com/Skaveza/KIVP';
const PORTFOLIO_URL = 'https://skaveza.github.io/io/';

const steps = [
  {
    icon: <Upload size={22} />,
    title: 'Upload',
    text: 'Add a photo or PDF of a receipt. PNG, JPG or PDF, up to 5MB.',
  },
  {
    icon: <ScanText size={22} />,
    title: 'Read',
    text: 'Text recognition and a fine-tuned LayoutLMv3 model extract the merchant, address, date and total.',
  },
  {
    icon: <Filter size={22} />,
    title: 'Filter',
    text: 'Receipts with a missing merchant, low confidence or an unusual total are set aside before scoring.',
  },
  {
    icon: <Gauge size={22} />,
    title: 'Score',
    text: 'The remaining receipts are scored out of 100. At 75 or above, the profile counts as verified.',
  },
];

const factors = [
  {
    name: 'Document quality',
    weight: 30,
    text: 'How confidently the model read each receipt.',
  },
  {
    name: 'Spending pattern',
    weight: 25,
    text: 'How much was spent and how many receipts there are, weighted by confidence in the totals.',
  },
  {
    name: 'Consistency',
    weight: 25,
    text: 'How regularly receipts appear over time, using the dates the model read.',
  },
  {
    name: 'Diversity',
    weight: 20,
    text: 'How many different merchants and locations appear.',
  },
];

const results = [
  { value: '0.95', label: 'Macro F1 on SROIE, a standard international receipt benchmark' },
  { value: '0.82', label: 'Macro F1 on simulated Kenyan receipts' },
  { value: '0.26', label: 'F1 for reading dates, the weakest field' },
  { value: 'Not yet', label: 'Tested on real Kenyan receipts' },
];

const faqs = [
  {
    q: 'What is KYC?',
    a: 'Know your customer: the checks a bank or investment platform runs to confirm who someone is and that their activity looks genuine. People without a formal credit history or payslips can find these checks hard to pass.',
  },
  {
    q: 'Is this a real product?',
    a: 'No. Uwezo KYC is a university capstone project built to test an idea. It is not offered to banks or lenders and must not be used for real credit or onboarding decisions.',
  },
  {
    q: 'Can I upload my own receipts?',
    a: 'Please upload sample receipts only. This is a research prototype, so do not upload anything containing personal or financial details you would not want stored.',
  },
  {
    q: 'Why can the first load take a minute?',
    a: 'The server runs on a free plan and goes to sleep when nobody is using it. The first request wakes it up.',
  },
  {
    q: 'Where can I see the code?',
    a: 'The full source, including the model training notebooks, is on GitHub.',
  },
];

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function ScoreCard() {
  const score = 83;
  const r = 52;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - score / 100);
  const bars = [
    ['Document quality', 90],
    ['Spending pattern', 76],
    ['Consistency', 80],
    ['Diversity', 85],
  ];

  return (
    <div className="relative">
      <div className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-moss/20 to-transparent blur-2xl" />
      <div className="relative rounded-3xl border border-black/5 bg-white p-7 shadow-[0_24px_60px_-20px_rgba(15,26,20,0.25)]">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-ink">Verification score</span>
          <span className="rounded-full bg-mint px-3 py-1 text-xs font-semibold text-moss">
            Verified
          </span>
        </div>

        <div className="mt-6 flex items-center gap-6">
          <div className="relative h-32 w-32 shrink-0">
            <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
              <circle cx="60" cy="60" r={r} fill="none" stroke="#E6F2EA" strokeWidth="10" />
              <circle
                cx="60"
                cy="60"
                r={r}
                fill="none"
                stroke="#0B6B3A"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={c}
                strokeDashoffset={offset}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-display text-4xl font-bold text-ink">{score}</span>
              <span className="text-xs text-ink/50">out of 100</span>
            </div>
          </div>

          <div className="flex-1 space-y-3">
            {bars.map(([label, value]) => (
              <div key={label}>
                <div className="mb-1 flex justify-between text-xs text-ink/70">
                  <span>{label}</span>
                  <span className="font-medium text-ink">{value}</span>
                </div>
                <div className="h-1.5 rounded-full bg-mint">
                  <div className="h-1.5 rounded-full bg-moss" style={{ width: `${value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between rounded-xl bg-sand px-4 py-3 text-xs text-ink/70">
          <span>12 receipts scored · 2 set aside</span>
          <span className="font-medium text-ink/50">Illustrative example</span>
        </div>
      </div>
    </div>
  );
}

export default function Home({ onSignIn, onRegister }) {
  return (
    <div className="min-h-screen bg-sand font-sans text-ink antialiased">
      {/* Navigation */}
      <header className="sticky top-0 z-20 border-b border-black/5 bg-sand/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="flex items-baseline gap-2">
            <span className="font-display text-2xl font-bold tracking-tight">Uwezo</span>
            <span className="text-xs font-semibold uppercase tracking-widest text-moss">KYC</span>
          </button>

          <nav className="hidden items-center gap-8 text-sm font-medium text-ink/70 md:flex">
            <button onClick={() => scrollTo('how')} className="hover:text-ink">How it works</button>
            <button onClick={() => scrollTo('scoring')} className="hover:text-ink">Scoring</button>
            <button onClick={() => scrollTo('limits')} className="hover:text-ink">Limits</button>
            <button onClick={() => scrollTo('faq')} className="hover:text-ink">FAQ</button>
          </nav>

          <div className="flex items-center gap-2">
            <button onClick={onSignIn} className="rounded-full px-4 py-2 text-sm font-medium hover:bg-black/5">
              Sign in
            </button>
            <button
              onClick={onRegister}
              className="rounded-full bg-ink px-5 py-2 text-sm font-semibold text-white transition hover:bg-moss"
            >
              Get started
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-6xl items-center gap-14 px-6 pb-20 pt-16 md:grid-cols-2 md:pt-24">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-moss/20 bg-mint px-3 py-1 text-xs font-semibold text-moss">
            <FlaskConical size={14} /> Research prototype
          </span>
          <h1 className="mt-6 font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl">
            Verification for people the credit system overlooks.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink/70">
            Uwezo KYC turns everyday receipts into a verification score, so people without a credit
            history or formal payslips have another way to show that their activity is genuine.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <button
              onClick={onRegister}
              className="group inline-flex items-center gap-2 rounded-full bg-moss px-7 py-3.5 font-semibold text-white shadow-lg shadow-moss/20 transition hover:bg-ink"
            >
              Try the prototype
              <ArrowRight size={18} className="transition group-hover:translate-x-0.5" />
            </button>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-ink/15 px-6 py-3.5 font-semibold hover:bg-white"
            >
              <Github size={18} /> View the code
            </a>
          </div>
          <p className="mt-6 text-sm text-ink/50">
            Built as a capstone project. Not for real credit or onboarding decisions.
          </p>
        </div>
        <ScoreCard />
      </section>

      {/* How it works */}
      <section id="how" className="scroll-mt-20 border-y border-black/5 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <p className="text-sm font-semibold uppercase tracking-widest text-moss">How it works</p>
          <h2 className="mt-3 max-w-2xl font-display text-4xl font-bold tracking-tight">
            From a photo of a receipt to a score, in four steps.
          </h2>
          <div className="mt-14 grid gap-6 md:grid-cols-4">
            {steps.map(({ icon, title, text }, i) => (
              <div key={title} className="relative rounded-2xl border border-black/5 bg-sand p-6">
                <div className="mb-5 flex items-center justify-between">
                  <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-moss shadow-sm">
                    {icon}
                  </span>
                  <span className="font-display text-3xl font-bold text-ink/15">0{i + 1}</span>
                </div>
                <h3 className="text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink/65">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scoring */}
      <section id="scoring" className="scroll-mt-20">
        <div className="mx-auto grid max-w-6xl gap-14 px-6 py-24 md:grid-cols-5">
          <div className="md:col-span-2">
            <p className="text-sm font-semibold uppercase tracking-widest text-moss">Scoring</p>
            <h2 className="mt-3 font-display text-4xl font-bold tracking-tight">
              Four signals, weighted into one score.
            </h2>
            <p className="mt-5 leading-relaxed text-ink/70">
              Each signal is scored from 0 to 100 and combined using the weights shown. The weights
              and the threshold of 75 are set by hand for this prototype. They have not been
              checked against real verification outcomes.
            </p>
          </div>
          <div className="space-y-4 md:col-span-3">
            {factors.map((f) => (
              <div key={f.name} className="flex gap-5 rounded-2xl border border-black/5 bg-white p-6">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-mint font-display text-xl font-bold text-moss">
                  {f.weight}%
                </div>
                <div>
                  <h3 className="font-semibold">{f.name}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-ink/65">{f.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Limits */}
      <section id="limits" className="scroll-mt-20 bg-ink text-white">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <p className="text-sm font-semibold uppercase tracking-widest text-emerald-300">
            Built with its limits in plain sight
          </p>
          <h2 className="mt-3 max-w-3xl font-display text-4xl font-bold tracking-tight">
            What the model can and cannot do today.
          </h2>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {results.map((x) => (
              <div key={x.label} className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="font-display text-4xl font-bold text-emerald-300">{x.value}</div>
                <p className="mt-3 text-sm leading-relaxed text-white/70">{x.label}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <ShieldCheck className="text-emerald-300" size={24} />
              <h3 className="mt-4 text-lg font-semibold">Accuracy</h3>
              <p className="mt-2 text-sm leading-relaxed text-white/70">
                The Kenyan results use simulated receipts, which are very regular, so they probably
                overstate real-world performance. Because dates are read least reliably, the
                consistency signal is the least dependable of the four.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
              <Lock className="text-emerald-300" size={24} />
              <h3 className="mt-4 text-lg font-semibold">Privacy</h3>
              <p className="mt-2 text-sm leading-relaxed text-white/70">
                Receipts and mobile money records are sensitive personal data. A real system would
                need clear consent, data minimisation and compliance with Kenya&rsquo;s Data
                Protection Act. This prototype has not been through that process, so please upload
                sample receipts only.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="scroll-mt-20">
        <div className="mx-auto max-w-3xl px-6 py-24">
          <p className="text-sm font-semibold uppercase tracking-widest text-moss">FAQ</p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight">Questions, answered plainly.</h2>
          <div className="mt-10 divide-y divide-black/10 border-y border-black/10">
            {faqs.map((f) => (
              <details key={f.q} className="group py-5">
                <summary className="flex cursor-pointer list-none items-center justify-between font-semibold">
                  {f.q}
                  <span className="ml-4 text-xl text-moss transition group-open:rotate-45">+</span>
                </summary>
                <p className="mt-3 leading-relaxed text-ink/70">{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Call to action */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="rounded-3xl bg-moss px-8 py-14 text-center text-white md:px-16">
          <h2 className="font-display text-4xl font-bold tracking-tight">See how it scores a receipt.</h2>
          <p className="mx-auto mt-4 max-w-xl text-white/80">
            Create a free account, upload a sample receipt and watch the pipeline run end to end.
          </p>
          <button
            onClick={onRegister}
            className="mt-8 inline-flex items-center gap-2 rounded-full bg-white px-8 py-3.5 font-semibold text-moss transition hover:bg-mint"
          >
            Try the prototype <ArrowRight size={18} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black/10">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-8 text-sm text-ink/60">
          <div>
            <span className="font-display text-lg font-bold text-ink">Uwezo</span>{' '}
            <span className="ml-1">KYC. A capstone project at African Leadership University.</span>
          </div>
          <div className="flex items-center gap-6">
            <span>Built by Sifa Kaveza Mwachoni</span>
            <a href={PORTFOLIO_URL} target="_blank" rel="noreferrer" className="font-medium text-ink hover:text-moss">
              Portfolio
            </a>
            <a href={GITHUB_URL} target="_blank" rel="noreferrer" className="font-medium text-ink hover:text-moss">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}