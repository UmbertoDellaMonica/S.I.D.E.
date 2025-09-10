import Link from "next/link";

export default async function HomePage() {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-gradient-to-br from-primary via-secondary to-accent">
      <main className="space-y-6 text-center px-4">
        <h1 className="text-4xl font-extrabold text-white drop-shadow-lg">
          Benvenuto in{" "}
          <span className="underline decoration-accent">S.I.D.E.</span>
        </h1>
        <p className="text-lg text-white/90">
          Gestisci la tua rete SCADA in maniera semplice e veloce.
        </p>

        <div className="mt-8 flex flex-col items-center justify-center gap-6 sm:flex-row">
          <Link
            href="/dashboard"
            className="rounded-lg bg-gray-900 px-8 py-3 font-semibold text-white shadow-lg transition duration-300 hover:scale-105 hover:bg-gray-800"
          >
            Login
          </Link>
        </div>
      </main>
    </div>
  );
}
