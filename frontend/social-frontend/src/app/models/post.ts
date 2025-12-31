export type ImageStatus = 'PENDING' | 'READY' | 'FAILED';

export interface Post {
  id: number;
  image_filename: string | null;   // filename or null
  image_status: ImageStatus;       // status of reduced image generation
  content: string | null;          // text or null
  username: string;
  created_at: string;              // ISO timestamp from backend
  image_description: string | null;
  description_status: 'NONE' | 'PENDING' | 'READY' | 'FAILED';
}
