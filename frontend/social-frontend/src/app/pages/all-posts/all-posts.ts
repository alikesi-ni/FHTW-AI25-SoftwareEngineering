import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PostService } from '../../services/post';
import { PostCard } from '../../components/post-card/post-card';

@Component({
  selector: 'app-all-posts',
  standalone: true,
  imports: [CommonModule, PostCard],
  templateUrl: './all-posts.html',
  styleUrls: ['./all-posts.css'],
})
export class AllPosts implements OnInit {

  posts: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private postService: PostService) {}

  ngOnInit(): void {
    this.loadPosts();
  }

  loadPosts(): void {
    this.error = null;

    this.postService.getAllPosts().subscribe({
      next: (res) => {
        this.posts = res ?? [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load posts', err);
        this.error = 'Failed to load posts.';
        this.loading = false;
      }
    });
  }
}
