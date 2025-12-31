import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PostService } from '../../services/post';
import { PostCard } from '../../components/post-card/post-card';
import {Post} from '../../models/post';

@Component({
  selector: 'app-all-posts',
  standalone: true,
  imports: [CommonModule, PostCard],
  templateUrl: './all-posts.html',
  styleUrls: ['./all-posts.css'],
})
export class AllPosts implements OnInit {

  posts: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private postService: PostService) {}

  ngOnInit(): void {
    this.loadPosts();
  }

  loadPosts(): void {
    this.error = null;

    this.postService.getAllPosts().subscribe({
      next: (res) => {
        this.posts = res ?? [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load posts', err);
        this.error = 'Failed to load posts.';
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
