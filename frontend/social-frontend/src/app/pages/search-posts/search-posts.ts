import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PostService } from '../../services/post';
import { Post } from '../../models/post';
import { PostCard } from '../../components/post-card/post-card';

@Component({
  selector: 'app-search-posts',
  standalone: true,
  imports: [CommonModule, FormsModule, PostCard],
  templateUrl: './search-posts.html',
  styleUrls: ['./search-posts.css']
})
export class SearchPosts {

  username = '';
  posts: Post[] = [];
  loading = false;
  error: string | null = null;

  constructor(private postService: PostService) {}

  search(): void {
    this.error = null;
    this.posts = [];

    const trimmed = this.username.trim();
    if (!trimmed) {
      this.error = 'Please enter a username.';
      return;
    }

    this.loading = true;

    this.postService.getPostsByUser(trimmed).subscribe({
      next: (res) => {
        this.posts = res ?? [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to search posts', err);
        this.error = 'Failed to search posts. Check backend.';
        this.loading = false;
      }
    });
  }
}
