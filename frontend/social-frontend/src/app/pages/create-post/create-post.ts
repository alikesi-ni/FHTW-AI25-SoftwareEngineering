import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PostService, CreatePostRequest } from '../../services/post';

@Component({
  selector: 'app-create-post',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './create-post.html',
  styleUrls: ['./create-post.css']
})
export class CreatePost {
  form: CreatePostRequest = {
    image: '',
    comment: '',
    username: ''
  };

  result: string | null = null;
  loading = false;
  error: string | null = null;

  constructor(private postService: PostService) {}

  submit() {
    this.error = null;
    this.result = null;
    this.loading = true;

    this.postService.createPost(this.form).subscribe({
      next: (res) => {
        this.loading = false;
        this.result = `Post created with ID: ${res.id}`;

        // RESET WORKS
        this.form = { image: '', comment: '', username: '' };
      },
      error: () => {
        this.loading = false;
        this.error = 'Failed to create post. Check backend.';
      }
    });
  }
}
