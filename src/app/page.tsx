import Link from 'next/link';
import { getAllPosts } from '@/lib/posts';

export default function Home() {
  const posts = getAllPosts();

  return (
    <div>
      <section className="hero-section">
        <h1 className="hero-title">Welcome to Daily Better</h1>
        <p className="hero-subtitle">가장 빠른 부와 성장의 지름길, 매일 조금씩 나아지는 습관</p>
      </section>

      <section>
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>최신 글</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {posts.map((post) => (
            <Link href={`/posts/${post.slug}`} key={post.slug}>
              <article className="post-card">
                <div className="post-meta">{post.date}</div>
                <h3 className="post-title">{post.title}</h3>
                <p className="post-excerpt">{post.excerpt}</p>
                {post.tags && (
                  <div className="tags-container">
                    {post.tags.map(tag => (
                      <span key={tag} className="tag">#{tag}</span>
                    ))}
                  </div>
                )}
              </article>
            </Link>
          ))}
          {posts.length === 0 && (
            <p style={{ color: 'var(--text-muted)' }}>아직 등록된 포스트가 없습니다.</p>
          )}
        </div>
      </section>
    </div>
  );
}
