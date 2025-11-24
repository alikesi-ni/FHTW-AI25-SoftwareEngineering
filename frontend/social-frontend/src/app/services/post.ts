import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Post } from '../models/post';

export interface CreatePostResponse {
  id: number;
  image_url?: string; // if you ever return it from backend
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
   * - comment: can be empty
   * - imageFile: optional (can be null)
   */
  createPost(
    username: string,
    comment: string,
    imageFile?: File | null
  ): Observable<CreatePostResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('comment', comment ?? '');

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
}
