import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { Post } from '../../models/post';
import { PostService } from '../../services/post';
import { PostCard } from '../../components/post-card/post-card';
import {
  DescriptionEventsService,
  DescriptionEventPayload,
} from '../../services/description-events';

@Component({
  selector: 'app-search-posts',
  standalone: true,
  imports: [CommonModule, FormsModule, PostCard],
  templateUrl: './search-posts.html',
})
export class SearchPosts implements OnDestroy {
  username = '';
  posts: Post[] = [];
  loading = false;
  error: string | null = null;

  private sseSubs = new Map<number, Subscription>();

  constructor(
    private postService: PostService,
    private descEvents: DescriptionEventsService
  ) {}

  ngOnDestroy(): void {
    for (const sub of this.sseSubs.values()) sub.unsubscribe();
    this.sseSubs.clear();
  }

  search(): void {
    const u = this.username.trim();
    if (!u) return;

    this.loading = true;
    this.error = null;

    this.postService.getPostsByUser(u).subscribe({
      next: (posts) => {
        this.posts = posts;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Failed to search posts.';
      },
    });
  }

  onGenerateDescription(postId: number): void {
    const post = this.posts.find((p) => p.id === postId);
    if (!post) return;

    // Guard rails
    if (!post.image_filename) return;
    if (post.description_status === 'PENDING') return;
    if (post.description_status === 'READY' && post.image_description) return;

    // Optimistic UI
    post.description_status = 'PENDING';
    post.image_description = null;

    // Trigger backend -> queue
    this.postService.requestImageDescription(postId).subscribe({
      next: () => {
        // Ensure we only have one SSE stream per post
        this.sseSubs.get(postId)?.unsubscribe();

        const sub = this.descEvents
          .subscribeToPost(postId)
          .subscribe((evt: DescriptionEventPayload) => {
            const p = this.posts.find((x) => x.id === postId);
            if (!p) return;

            if (evt.description_status) {
              p.description_status = evt.description_status as Post['description_status'];
            }
            if (evt.image_description !== undefined) {
              p.image_description = evt.image_description ?? null;
            }

            // Close SSE stream on terminal state
            if (p.description_status === 'READY' || p.description_status === 'FAILED') {
              sub.unsubscribe();
              this.sseSubs.delete(postId);
            }
          });

        this.sseSubs.set(postId, sub);
      },
      error: () => {
        // Backend unavailable / request failed
        post.description_status = 'FAILED';
        this.sseSubs.get(postId)?.unsubscribe();
        this.sseSubs.delete(postId);
      },
    });
  }
}
