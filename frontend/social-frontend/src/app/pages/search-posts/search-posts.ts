import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription, switchMap } from 'rxjs';

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

    // clean up old SSE streams when running a new search
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

  onDescribeImage(postId: number): void {
    const post = this.posts.find((p) => p.id === postId);
    if (!post) return;

    // Guard rails
    if (!post.image_filename) return;
    if (post.description_status === 'PENDING') return;
    if (post.description_status === 'READY' && post.image_description) return;

    // Optimistic UI
    this.patchPost(postId, {
      description_status: 'PENDING',
      image_description: null,
    });

    this.postService.requestImageDescription(postId).subscribe({
      next: () => {
        this.sseSubs.get(postId)?.unsubscribe();

        // placeholder subscription FIRST (avoids "sub before init" on sync emission)
        const holder = new Subscription();
        this.sseSubs.set(postId, holder);

        const inner = this.descEvents
          .subscribeToPost(postId)
          .subscribe((evt: DescriptionEventPayload) => {
            const p = this.posts.find((x) => x.id === postId);
            if (!p) return;

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

            const updated = this.posts.find((x) => x.id === postId);
            if (
              updated &&
              (updated.description_status === 'READY' ||
                updated.description_status === 'FAILED')
            ) {
              this.sseSubs.get(postId)?.unsubscribe();
              this.sseSubs.delete(postId);
            }
          });

        holder.add(inner);
      },
      error: (err) => {
        console.error(err);
        this.patchPost(postId, { description_status: 'FAILED' });
        this.sseSubs.get(postId)?.unsubscribe();
        this.sseSubs.delete(postId);
      },
    });
  }

  onAnalyzeSentiment(postId: number): void {
    const post = this.posts.find((p) => p.id === postId);
    if (!post) return;

    // Guard rails
    if (!post.content) return;
    if (post.sentiment_status === 'PENDING') return;
    if (post.sentiment_status === 'READY' && post.sentiment_label && post.sentiment_score !== null) return;

    // Optimistic UI
    this.patchPost(postId, { sentiment_status: 'PENDING' });

    this.postService
      .analyzeSentiment(postId)
      .pipe(switchMap(() => this.postService.pollSentiment(postId)))
      .subscribe({
        next: (updated) => this.replacePost(updated),
        error: (err) => {
          console.error(err);
          this.patchPost(postId, { sentiment_status: 'FAILED' });
        },
      });
  }

  // helpers
  replacePost(updated: Post): void {
    this.posts = this.posts.map((p) => (p.id === updated.id ? updated : p));
  }

  patchPost(postId: number, patch: Partial<Post>): void {
    this.posts = this.posts.map((p) => (p.id === postId ? { ...p, ...patch } : p));
  }
}
