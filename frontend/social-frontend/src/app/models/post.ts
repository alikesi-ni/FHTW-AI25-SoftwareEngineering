export interface Post {
  id: number;
  image: string | null;      // filename or null
  comment: string | null;    // text or null
  username: string;
  created_at: string;        // ISO timestamp from backend
}
