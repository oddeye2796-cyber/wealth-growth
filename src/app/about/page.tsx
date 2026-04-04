import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="container" style={{ padding: '4rem 2rem' }}>
      <section className="hero-section" style={{ marginBottom: '5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '3.5rem', letterSpacing: '-1.5px' }}>
          Daily Better
        </h1>
        <p className="hero-subtitle" style={{ fontSize: '1.4rem' }}>
          어제보다 나은 나를 만드는 오늘의 기록
        </p>
      </section>

      <div className="markdown-body">
        <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem', color: '#fff' }}>우리만의 비전</h2>
        <p>
          복잡한 세상 속에서 우리는 매일 수많은 정보를 마주합니다. <strong>Daily Better</strong>는 그 정보의 홍수 속에서 
          진취적이고 의미 있는 삶을 살고자 하는 분들을 위해 탄생했습니다.
        </p>

        <div style={{ 
          background: 'var(--card-bg)', 
          border: '1px solid var(--card-border)', 
          borderRadius: '24px', 
          padding: '2.5rem',
          marginTop: '3rem',
          marginBottom: '3rem',
          backdropFilter: 'blur(10px)'
        }}>
          <h3 style={{ marginTop: 0, color: 'var(--primary-hover)' }}>핵심 가치 (Core Values)</h3>
          <ul style={{ listStyle: 'none', marginLeft: 0, marginTop: '1.5rem' }}>
            <li style={{ marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>💡</span>
              <span><strong>통찰력 있는 재테크:</strong> 단순한 돈 벌기를 넘어, 자산을 지키고 키우는 지혜를 공유합니다.</span>
            </li>
            <li style={{ marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>🌱</span>
              <span><strong>지속 가능한 자기계발:</strong> 벼락치기가 아닌, 평생의 습관으로 남을 내공을 추구합니다.</span>
            </li>
            <li style={{ marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>🤖</span>
              <span><strong>AI와 인간의 협업:</strong> 미래 기술인 AI를 활용해 더 빠르고 효율적인 통찰을 제공합니다.</span>
            </li>
          </ul>
        </div>

        <h2 style={{ fontSize: '2rem', marginTop: '4rem' }}>왜 시작했나요?</h2>
        <p>
          혼자 공부하고 실천하는 과정은 때로 외롭고 속도가 더딜 수 있습니다. 
          저희는 AI의 폭발적인 기술력과 인간의 따뜻한 통찰력을 결합하여, 
          가장 효율적인 학습 경로와 실행 동기를 제공하고자 합니다.
        </p>
        <p>
          재테크 실무, 독서 습관, 마인드셋 트레이닝까지 — 
          <strong>Daily Better</strong>와 함께라면 어제와는 다른 오늘을 만나실 수 있습니다.
        </p>

        <div style={{ textAlign: 'center', marginTop: '6rem' }}>
          <Link href="/" className="post-card" style={{ 
            display: 'inline-block', 
            padding: '1.2rem 3rem', 
            borderRadius: '50px',
            background: 'linear-gradient(135deg, var(--primary), #a78bfa)',
            color: '#fff',
            fontWeight: 700,
            fontSize: '1.1rem',
            border: 'none',
            boxShadow: '0 10px 30px rgba(59, 130, 246, 0.3)'
          }}>
            블로그 글 보러가기 →
          </Link>
        </div>
      </div>
    </div>
  );
}
