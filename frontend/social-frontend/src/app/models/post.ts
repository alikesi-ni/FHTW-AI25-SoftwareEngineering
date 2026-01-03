export type ImageStatus = 'PENDING' | 'READY' | 'FAILED';

export type SentimentStatus = 'NONE' | 'PENDING' | 'READY' | 'FAILED';

export interface Post {
  id: number;
  image_filename: string | null;   // filename or null
  image_status: ImageStatus;       // status of reduced image generation
  content: string | null;          // text or null
  username: string;
  created_at: string;
  
  sentiment_status: SentimentStatus;
  sentiment_label: string | null;
  sentiment_score: number | null;// ISO timestamp from backend
}
