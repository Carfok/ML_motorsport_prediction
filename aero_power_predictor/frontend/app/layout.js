import './globals.css';

export const metadata = {
  title: 'The 2026 Aero-Power Predictor',
  description: 'AI-powered F1 performance prediction system',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-slate-950 text-white antialiased">
        {children}
      </body>
    </html>
  );
}
