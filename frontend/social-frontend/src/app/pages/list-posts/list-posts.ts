import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PostService } from '../../services/post';

@Component({
  selector: 'app-list-posts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './list-posts.html',
  styleUrls: ['./list-posts.css']
})
export class ListPosts implements OnInit {

  posts: any[] = [];
  loading = false;
  error: string | null = null;

  constructor(private postService: PostService) {}

  ngOnInit() {
    this.loadPosts();
  }

  loadPosts() {
    this.loading = true;
    this.error = null;

    this.postService.getAllPosts().subscribe({
      next: (res) => {
        this.posts = res;
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load posts.';
        this.loading = false;
      }
    });
  }
}
