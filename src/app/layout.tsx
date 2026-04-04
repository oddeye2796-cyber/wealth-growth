import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from 'next/link';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Daily Better | 어제보다 나은 하루",
  description: "매일 성장하는 재테크와 자기계발 인사이트",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <header className="header">
          <Link href="/" className="logo">Daily Better</Link>
          <nav style={{display: 'flex', gap: '1rem'}}>
            <Link href="/" style={{color: 'var(--text-muted)', fontWeight: 500}}>Home</Link>
            <Link href="/about" style={{color: 'var(--text-muted)', fontWeight: 500}}>About</Link>
          </nav>
        </header>
        <main className="container">
          {children}
        </main>
      </body>
    </html>
  );
}
