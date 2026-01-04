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

  onGenerateDescription(postId: number) {
    // optimistic UI update
    this.patchPost(postId, { description_status: 'PENDING' });

    // enqueue description job
    this.postService.describePost(postId).subscribe({
      next: () => this.pollPost(postId),
      error: (err) => console.error(err),
    });
  }

  pollPost(postId: number) {
    const maxAttempts = 20;
    let attempts = 0;

    const tick = () => {
      attempts++;

      this.postService.getPost(postId).subscribe({
        next: (post) => {
          this.replacePost(post);

          if (
            post.description_status === 'READY' ||
            post.description_status === 'FAILED' ||
            attempts >= maxAttempts
          ) {
            return; // stop polling
          }

          setTimeout(tick, 1500);
        },
        error: () => {
          if (attempts < maxAttempts) {
            setTimeout(tick, 2000);
          }
        },
      });
    };

    tick();
  }

  // helpers
  replacePost(updated: Post) {
    this.posts = this.posts.map((p) =>
      p.id === updated.id ? updated : p
    );
  }

  patchPost(postId: number, patch: Partial<Post>) {
    this.posts = this.posts.map((p) =>
      p.id === postId ? { ...p, ...patch } : p
    );
  }
}
