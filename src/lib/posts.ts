import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

// Next.js App Router에서는 process.cwd() 기준으로 경로를 잡습니다.
const postsDirectory = path.join(process.cwd(), 'src', 'content');

export interface PostMetaData {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  tags?: string[];
  coverImage?: string;
}

export interface Post extends PostMetaData {
  content: string;
}

export function getPostSlugs() {
  if (!fs.existsSync(postsDirectory)) {
    fs.mkdirSync(postsDirectory, { recursive: true });
    return [];
  }
  return fs.readdirSync(postsDirectory).filter(file => file.endsWith('.md'));
}

export function getPostBySlug(slug: string): Post {
  const realSlug = slug.replace(/\.md$/, '');
  const fullPath = path.join(postsDirectory, `${realSlug}.md`);
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  
  // gray-matter를 이용해 frontmatter(메타데이터)와 content를 분리합니다.
  const { data, content } = matter(fileContents);

  return {
    slug: realSlug,
    title: data.title || '제목 없음',
    date: data.date || '',
    excerpt: data.excerpt || '',
    tags: data.tags || [],
    coverImage: data.coverImage || '',
    content,
  };
}

export function getAllPosts(): Post[] {
  const slugs = getPostSlugs();
  const posts = slugs
    .map((slug) => getPostBySlug(slug))
    // 최신 날짜순 정렬
    .sort((post1, post2) => (post1.date > post2.date ? -1 : 1));
  return posts;
}
