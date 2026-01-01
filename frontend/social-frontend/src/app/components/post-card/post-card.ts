import { Component, Input, Output, EventEmitter, HostListener } from '@angular/core';
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

  // NEW (minimal): bubble up "generate description" request to parent
  @Output() generateDescription = new EventEmitter<number>();

  lightboxOpen = false;

  // If reduced image fails to load, we fall back to the original once.
  imgSrc: string | null = null;
  private triedFallback = false;

  ngOnChanges() {
    this.imgSrc = this.thumbUrl;
    this.triedFallback = false;
  }

  // NEW (minimal): expose description to template
  get imageDescription(): string | null {
    return this.post.image_description ?? null;
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

  // NEW (minimal): called by the "Generate description" button in template
  requestDescription(event: MouseEvent) {
    event.stopPropagation();
    this.generateDescription.emit(this.post.id);
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
}
