import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription, switchMap } from 'rxjs';

import { PostService } from '../../services/post';
import { PostCard } from '../../components/post-card/post-card';
import { Post } from '../../models/post';
import {
  DescriptionEventsService,
  DescriptionEventPayload,
} from '../../services/description-events';

@Component({
  selector: 'app-all-posts',
  standalone: true,
  imports: [CommonModule, PostCard],
  templateUrl: './all-posts.html',
  styleUrls: ['./all-posts.css'],
})
export class AllPosts implements OnInit, OnDestroy {
  posts: Post[] = [];
  loading = true;
  error: string | null = null;

  private sseSubs = new Map<number, Subscription>();

  constructor(
    private postService: PostService,
    private descEvents: DescriptionEventsService
  ) {}

  ngOnInit(): void {
    this.loadPosts();
  }

  ngOnDestroy(): void {
    for (const sub of this.sseSubs.values()) sub.unsubscribe();
    this.sseSubs.clear();
  }

  loadPosts(): void {
    this.error = null;
    this.loading = true;

    this.postService.getAllPosts().subscribe({
      next: (res) => {
        this.posts = res ?? [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load posts', err);
        this.error = 'Failed to load posts.';
        this.loading = false;
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
        // Kill any existing stream for this post
        this.sseSubs.get(postId)?.unsubscribe();

        // IMPORTANT: create placeholder BEFORE subscribing (avoids TDZ / sync emission issues)
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
              // Unsubscribe via map (never reference local const sub inside callback)
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
