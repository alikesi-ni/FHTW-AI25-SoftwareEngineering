import { Component, Input } from '@angular/core';
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

  get imageUrl(): string | null {
    if (!this.post.image) {
      return null;
    }
    return `http://localhost:8000/static/${this.post.image}`;
  }
}
