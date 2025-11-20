import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CreatePostRequest {
  image: string;
  comment: string;
  username: string;
}

@Injectable({
  providedIn: 'root'
})
export class PostService {

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  createPost(data: CreatePostRequest): Observable<{ id: number }> {
    return this.http.post<{ id: number }>(`${this.apiUrl}/posts`, data);
  }

  getAllPosts() {
  return this.http.get<any[]>('http://localhost:8000/posts');
}

}
