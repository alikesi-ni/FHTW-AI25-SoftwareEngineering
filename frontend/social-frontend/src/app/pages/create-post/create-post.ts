import { Component, ElementRef, ViewChild } from '@angular/core';
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
  @ViewChild('imageInput') imageInput?: ElementRef<HTMLInputElement>;

  form = {
    content: '',
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

  private clearFileInput() {
    this.selectedFile = null;
    if (this.imageInput?.nativeElement) {
      this.imageInput.nativeElement.value = '';
    }
  }

  canSubmit(): boolean {
    const usernameOk = this.form.username.trim().length > 0;
    const hasContent = this.form.content.trim().length > 0;
    const hasImage = !!this.selectedFile;
    return usernameOk && (hasContent || hasImage);
  }

  submit() {
    this.error = null;
    this.result = null;

    const username = this.form.username.trim();
    const content = this.form.content.trim();
    const hasContent = content.length > 0;
    const hasImage = !!this.selectedFile;

    if (!username) {
      this.error = 'Username is required.';
      return;
    }

    if (!hasContent && !hasImage) {
      this.error = 'Please provide at least some content or an image.';
      return;
    }

    this.loading = true;

    this.postService
      .createPost(username, content, this.selectedFile)
      .subscribe({
        next: (res) => {
          this.loading = false;
          this.result = `Post created with ID: ${res.id}`;

          // Reset form + clear file input UI
          this.form = { content: '', username: '' };
          this.clearFileInput();
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
