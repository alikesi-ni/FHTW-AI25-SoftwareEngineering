import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CreatePostRequest {
  image: string;
  comment: string;
  username: string;
}

export interface CreatePostWithImageResponse {
  id: number;
  image_path: string;
}

@Injectable({
  providedIn: 'root'
})
export class PostService {

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  // Old JSON endpoint (if you still want it)
  createPost(data: CreatePostRequest): Observable<{ id: number }> {
    return this.http.post<{ id: number }>(`${this.apiUrl}/posts`, data);
  }

  // New: use multipart/form-data to hit /posts/with-image
  createPostWithImage(
    username: string,
    comment: string,
    imageFile: File
  ): Observable<CreatePostWithImageResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('comment', comment);
    formData.append('image', imageFile); // name must be "image"

    return this.http.post<CreatePostWithImageResponse>(
      `${this.apiUrl}/posts`,
      formData
    );
  }

  getAllPosts() {
    return this.http.get<any[]>(`${this.apiUrl}/posts`);
  }

  getPostsByUser(username: string) {
    return this.http.get<any[]>(`${this.apiUrl}/posts`, {
      params: {
        user: username
      }
    });
  }
}
