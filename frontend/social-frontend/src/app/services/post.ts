import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Post } from '../models/post';

export interface CreatePostResponse {
  id: number;
  original_url?: string;
  reduced_url?: string;
}

@Injectable({
  providedIn: 'root'
})
export class PostService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  /**
   * Create a post using multipart/form-data.
   * - username: required
   * - content: can be empty (but then image must be present)
   * - imageFile: optional (can be null)
   */
  createPost(
    username: string,
    content: string,
    imageFile?: File | null
  ): Observable<CreatePostResponse> {
    const formData = new FormData();
    formData.append('username', username);

    const trimmed = (content ?? '').trim();
    if (trimmed.length > 0) {
      formData.append('content', trimmed);
    }

    if (imageFile) {
      formData.append('image', imageFile);
    }

    return this.http.post<CreatePostResponse>(
      `${this.apiUrl}/posts`,
      formData
    );
  }

  getAllPosts(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.apiUrl}/posts`);
  }

  getPostsByUser(username: string): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.apiUrl}/posts`, {
      params: {
        user: username,
        order_by: 'created_at',
        order_dir: 'desc'
      }
    });
  }

  analyzeSentiment(postId: number) {
    const url = `${this.apiUrl}/posts/${postId}/sentiment`;
    return this.http.post<Post>(url, {});
  }

  getPost(postId: number): Observable<Post> {
    return this.http.get<Post>(`${this.apiUrl}/posts/${postId}`);
  }

  describePost(postId: number): Observable<{ status: string }> {
    return this.http.post<{ status: string }>(
      `${this.apiUrl}/posts/${postId}/describe`,
      {}
    );
  }
}
