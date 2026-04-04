'use client';

import { useEffect, useRef } from 'react';

export default function GuestbookPage() {
  const commentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.setAttribute('data-repo', 'oddeye2796-cyber/wealth-growth'); 
    script.setAttribute('data-repo-id', 'R_kgDOR5eQ9Q'); 
    script.setAttribute('data-category', 'Announcements');
    script.setAttribute('data-category-id', 'DIC_kwDOR5eQ9c4C6Cuq');
    script.setAttribute('data-mapping', 'pathname');
    script.setAttribute('data-strict', '0');
    script.setAttribute('data-reactions-enabled', '1');
    script.setAttribute('data-emit-metadata', '0');
    script.setAttribute('data-input-position', 'bottom');
    script.setAttribute('data-theme', 'dark_dimmed');
    script.setAttribute('data-lang', 'ko');
    script.setAttribute('crossorigin', 'anonymous');
    script.async = true;

    if (commentRef.current) {
      commentRef.current.appendChild(script);
    }

    return () => {
      const giscus = document.querySelector('.giscus');
      if (giscus) giscus.remove();
    };
  }, []);

  return (
    <div className="container" style={{ padding: '4rem 2rem' }}>
      <section className="hero-section">
        <h1 className="hero-title">방명록</h1>
        <p className="hero-subtitle">방문해주셔서 감사합니다. 자유롭게 의견을 남겨주세요!</p>
      </section>

      <div style={{ marginTop: '3rem' }}>
        <div ref={commentRef} id="giscus-container" />
      </div>
      
      <div style={{ marginTop: '4rem', padding: '2rem', background: 'var(--card-bg)', borderRadius: '16px', border: '1px solid var(--card-border)' }}>
        <h3 style={{ marginBottom: '1rem' }}>💡 안내사항</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          방명록은 GitHub Discussions를 통해 운영됩니다. 댓글을 남기려면 GitHub 로그인이 필요합니다. 
          건전한 소통 문화를 위해 비방이나 광고성 글은 삭제될 수 있습니다.
        </p>
      </div>
    </div>
  );
}
