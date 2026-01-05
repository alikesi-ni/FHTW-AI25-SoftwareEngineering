import {
  Component,
  Input,
  Output,
  EventEmitter,
  HostListener,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Post } from '../../models/post';

@Component({
  selector: 'app-post-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './post-card.html',
  styleUrls: ['./post-card.css'],
})
export class PostCard {
  @Input({ required: true }) post!: Post;

  /**
   * Dumb UI outputs:
   * Parents decide what "request" means (HTTP, SSE subscribe, polling, etc.)
   */
  @Output() describeImage = new EventEmitter<number>();
  @Output() analyzeSentiment = new EventEmitter<number>();

  lightboxOpen = false;

  // If reduced image fails to load, we fall back to the original once.
  imgSrc: string | null = null;
  private triedFallback = false;

  ngOnChanges() {
    this.imgSrc = this.thumbUrl;
    this.triedFallback = false;
  }

  get originalUrl(): string | null {
    if (!this.post.image_filename) return null;
    return `http://localhost:8000/static/original/${this.post.image_filename}`;
  }

  get reducedUrl(): string | null {
    if (!this.post.image_filename) return null;
    return `http://localhost:8000/static/reduced/${this.post.image_filename}`;
  }

  // Show reduced by default only when READY; otherwise show original (processing/failed).
  get thumbUrl(): string | null {
    if (!this.post.image_filename) return null;
    if (this.post.image_status === 'READY') return this.reducedUrl;
    return this.originalUrl;
  }

  onImgError() {
    // If reduced isn't there yet (or 404), fall back to original once.
    if (!this.triedFallback && this.originalUrl && this.imgSrc !== this.originalUrl) {
      this.triedFallback = true;
      this.imgSrc = this.originalUrl;
      return;
    }
    // If even original fails, hide image.
    this.imgSrc = null;
  }

  get imageDescription(): string | null {
    return (this.post.image_description ?? '').trim() || null;
  }

  get sentimentAvailable(): boolean {
    return (
      this.post.sentiment_status === 'READY' &&
      !!this.post.sentiment_label &&
      this.post.sentiment_score !== null &&
      this.post.sentiment_score !== undefined
    );
  }

  get showSentimentButton(): boolean {
    // Only show the button if there's content AND no sentiment available yet.
    return !!this.post.content && !this.sentimentAvailable;
  }

  /**
   * Emitters (no HTTP here)
   */
  requestDescription(ev: Event) {
    ev.stopPropagation();
    if (!this.post?.id) return;
    this.describeImage.emit(this.post.id);
  }

  requestSentiment(ev: Event) {
    ev.stopPropagation();
    if (!this.post?.id) return;
    this.analyzeSentiment.emit(this.post.id);
  }

  /**
   * Lightbox
   */
  openLightbox() {
    if (!this.originalUrl) return;
    this.lightboxOpen = true;
    document.body.style.overflow = 'hidden';
  }

  closeLightbox() {
    this.lightboxOpen = false;
    document.body.style.overflow = '';
  }

  @HostListener('document:keydown.escape')
  onEsc() {
    if (this.lightboxOpen) this.closeLightbox();
  }

  /**
   * Created-at formatting: show to minutes in user's local timezone
   */
  get createdAtDisplay(): string {
    const raw = this.post?.created_at;
    if (!raw) return '';
    const d = new Date(raw);
    if (Number.isNaN(d.getTime())) return raw;

    // uses user's local timezone automatically
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  }
}
