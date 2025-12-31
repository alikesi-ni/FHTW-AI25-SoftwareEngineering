import { Component, EventEmitter, Input, Output } from '@angular/core';
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

  @Output() generateDescription = new EventEmitter<number>();

  lightboxOpen = false;

  private imgFailed = false;

  get originalUrl(): string | null {
    if (!this.post.image_filename) return null;
    return `http://localhost:8000/static/original/${this.post.image_filename}`;
  }

  get reducedUrl(): string | null {
    if (!this.post.image_filename) return null;
    return `http://localhost:8000/static/reduced/${this.post.image_filename}`;
  }

  // show reduced when READY; otherwise show original as fallback
  get imgSrc(): string | null {
    if (!this.post.image_filename) return null;

    if (this.imgFailed) {
      return this.originalUrl;
    }

    if (this.post.image_status === 'READY') {
      return this.reducedUrl;
    }

    // PENDING/FAILED -> show original (worker may not have reduced yet)
    return this.originalUrl;
  }

  get hasImage(): boolean {
    return !!this.post.image_filename;
  }

  get hasImageDescription(): boolean {
    return !!(this.post as any).image_description;
  }

  get imageDescription(): string | null {
    return ((this.post as any).image_description ?? null) as string | null;
  }

  onImgError() {
    this.imgFailed = true;
  }

  openLightbox() {
    if (!this.originalUrl) return;
    this.lightboxOpen = true;
  }

  closeLightbox() {
    this.lightboxOpen = false;
  }

  requestDescription(event: MouseEvent) {
    // don't trigger the image lightbox when clicking this action
    event.stopPropagation();
    this.generateDescription.emit(this.post.id);
  }
}
