export type ImageStatus = 'PENDING' | 'READY' | 'FAILED';

export type SentimentStatus = 'NONE' | 'PENDING' | 'READY' | 'FAILED';

export interface Post {
  id: number;

  /* Image */
  image_filename: string | null;
  image_status: 'PENDING' | 'READY' | 'FAILED';

  /* Post content */
  content: string | null;
  username: string;
  created_at: string;

  /* AI image description */
  image_description: string | null;
  description_status: 'NONE' | 'PENDING' | 'READY' | 'FAILED';

  /* Sentiment analysis */
  sentiment_status: 'NONE' | 'PENDING' | 'READY' | 'FAILED';
  sentiment_label: string | null;
  sentiment_score: number | null;
}

