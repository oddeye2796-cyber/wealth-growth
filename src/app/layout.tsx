import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from 'next/link';
import NewsletterForm from '@/components/NewsletterForm';
import VisitorCounter from '@/components/VisitorCounter';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "Daily Better | 어제보다 나은 하루",
    template: "%s | Daily Better"
  },
  description: "매일 성장하는 재테크와 자기계발 인사이트. 어제보다 더 나은 당신을 위한 정보를 기록합니다.",
  keywords: ["재테크", "자기계발", "경제자유", "부자마인드", "동기부여", "AI자동화"],
  authors: [{ name: "Daily Better" }],
  openGraph: {
    title: "Daily Better | 어제보다 나은 하루",
    description: "매일 성장하는 재테크와 자기계발 인사이트",
    url: "https://wealth-growth.vercel.app",
    siteName: "Daily Better",
    locale: "ko_KR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Daily Better | 어제보다 나은 하루",
    description: "매일 성장하는 재테크와 자기계발 인사이트",
  },
  robots: {
    index: true,
    follow: true,
  }
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
          <nav style={{display: 'flex', gap: '1.5rem', alignItems: 'center'}}>
            <Link href="/" style={{color: 'var(--text-muted)', fontWeight: 500}}>Home</Link>
            <Link href="/about" style={{color: 'var(--text-muted)', fontWeight: 500}}>About</Link>
            <Link href="/guestbook" style={{color: 'var(--text-muted)', fontWeight: 500}}>Guestbook</Link>
          </nav>
        </header>
        
        <main className="container">
          {children}
        </main>

        <footer className="footer">
          <div className="container">
            <div className="footer-content">
              <div className="footer-info">
                <h3>Daily Better</h3>
                <p>매일 조금씩 더 나은 내일을 위해 기록합니다.</p>
                <div className="footer-links">
                  <Link href="/about">About</Link>
                  <Link href="/guestbook">Guestbook</Link>
                </div>
              </div>
              
              <NewsletterForm />
            </div>
            
            <div className="footer-bottom">
              <VisitorCounter />
              <p>© {new Date().getFullYear()} Daily Better. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
