import { Routes } from '@angular/router';
import { CreatePost } from './pages/create-post/create-post';
import { AllPosts } from './pages/all-posts/all-posts';
import { SearchPosts } from './pages/search-posts/search-posts';

export const routes: Routes = [
  { path: 'create-post', component: CreatePost },
  { path: 'all-posts', component: AllPosts },
  { path: 'search-posts', component: SearchPosts },
  { path: '', redirectTo: 'all-posts', pathMatch: 'full' }
];


