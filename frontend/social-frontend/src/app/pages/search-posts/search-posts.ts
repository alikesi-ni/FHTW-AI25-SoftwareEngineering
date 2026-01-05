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

    for (const sub of this.sseSubs.values()) sub.unsubscribe();
    this.sseSubs.clear();

    this.postService.getPostsByUser(u).subscribe({
      next: (posts) => {
        this.posts = posts ?? [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Failed to search posts.';
      },
    });
  }

  /* ---------------- IMAGE DESCRIPTION ---------------- */

  onDescribeImage(postId: number): void {
    const post = this.posts.find((p) => p.id === postId);
    if (!post || !post.image_filename) return;

    if (post.description_status === 'PENDING') return;
    if (post.description_status === 'READY' && post.image_description) return;

    this.patchPost(postId, {
      description_status: 'PENDING',
      image_description: null,
    });

    this.postService.requestImageDescription(postId).subscribe({
      next: () => {
        this.sseSubs.get(postId)?.unsubscribe();

        const sub = this.descEvents
          .subscribeToPost(postId)
          .subscribe((evt: DescriptionEventPayload) => {
            if (evt.description_status) {
              this.patchPost(postId, {
                description_status: evt.description_status as Post['description_status'],
              });
            }
            if (evt.image_description !== undefined) {
              this.patchPost(postId, {
                image_description: evt.image_description ?? null,
              });
            }

            const updated = this.posts.find((p) => p.id === postId);
            if (
              updated &&
              (updated.description_status === 'READY' ||
                updated.description_status === 'FAILED')
            ) {
              sub.unsubscribe();
              this.sseSubs.delete(postId);
            }
          });

        this.sseSubs.set(postId, sub);
      },
      error: () => {
        this.patchPost(postId, { description_status: 'FAILED' });
      },
    });
  }

  /* ---------------- SENTIMENT ---------------- */

  onAnalyzeSentiment(postId: number): void {
    const post = this.posts.find((p) => p.id === postId);
    if (!post || !post.content) return;

    if (post.sentiment_status === 'PENDING') return;
    if (post.sentiment_status === 'READY') return;

    this.patchPost(postId, { sentiment_status: 'PENDING' });

    this.postService.analyzeSentiment(postId).subscribe({
      next: () => {
        this.postService.pollSentiment(postId).subscribe({
          next: (updated) => {
            this.patchPost(postId, {
              sentiment_status: updated.sentiment_status,
              sentiment_label: updated.sentiment_label,
              sentiment_score: updated.sentiment_score,
            });
          },
          error: () => {
            this.patchPost(postId, { sentiment_status: 'FAILED' });
          },
        });
      },
      error: () => {
        this.patchPost(postId, { sentiment_status: 'FAILED' });
      },
    });
  }

  /* ---------------- HELPERS ---------------- */

  patchPost(postId: number, patch: Partial<Post>): void {
    this.posts = this.posts.map((p) =>
      p.id === postId ? { ...p, ...patch } : p
    );
  }
}
