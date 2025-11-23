import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PostService } from '../../services/post';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-create-post',
  standalone: true,
  imports: [FormsModule,CommonModule],
  templateUrl: './create-post.html',
  styleUrls: ['./create-post.css']
})
export class CreatePost {
  // Only comment + username are bound via ngModel now
  form = {
    comment: '',
    username: ''
  };

  // Holds the selected file from the <input type="file">
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

  submit() {
    this.error = null;
    this.result = null;

    if (!this.selectedFile) {
      this.error = 'Please select an image file.';
      return;
    }

    if (!this.form.username) {
      this.error = 'Username is required.';
      return;
    }

    this.loading = true;

    this.postService
      .createPostWithImage(this.form.username, this.form.comment, this.selectedFile)
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
