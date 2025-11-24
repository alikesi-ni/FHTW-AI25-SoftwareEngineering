import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PostService } from '../../services/post';

@Component({
  selector: 'app-create-post',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './create-post.html',
  styleUrls: ['./create-post.css']
})
export class CreatePost {
  form = {
    comment: '',
    username: ''
  };

  selectedFile: File | null = null;

  result: string | null = null;
  loading = false;
  error: string | null = null;

  constructor(private postService: PostService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      this.selectedFile = null;
      return;
    }
    this.selectedFile = input.files[0];
    this.error = null;
  }

  // Username must be non-empty,
  // and either a comment or an image (or both) must be present
  canSubmit(): boolean {
    const usernameOk = this.form.username.trim().length > 0;
    const hasComment = this.form.comment.trim().length > 0;
    const hasImage = !!this.selectedFile;
    return usernameOk && (hasComment || hasImage);
  }

  submit() {
    this.error = null;
    this.result = null;

    const username = this.form.username.trim();
    const comment = this.form.comment.trim();
    const hasComment = comment.length > 0;
    const hasImage = !!this.selectedFile;

    if (!username) {
      this.error = 'Username is required.';
      return;
    }

    if (!hasComment && !hasImage) {
      this.error = 'Please provide at least a comment or an image.';
      return;
    }

    this.loading = true;

    this.postService
      .createPost(username, comment, this.selectedFile)
      .subscribe({
        next: (res) => {
          this.loading = false;
          this.result = `Post created with ID: ${res.id}`;

          // Reset form + file
          this.form = { comment: '', username: '' };
          this.selectedFile = null;
        },
        error: (err) => {
          this.loading = false;
          if (err.error?.detail) {
            this.error = err.error.detail;
          } else {
            this.error = 'Failed to create post. Check backend.';
          }
        }
      });
  }
}
