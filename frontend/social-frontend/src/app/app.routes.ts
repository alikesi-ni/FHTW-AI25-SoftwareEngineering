import { Routes } from '@angular/router';
import { CreatePost } from './pages/create-post/create-post';
import { ListPosts } from './pages/list-posts/list-posts';
import { SearchPosts } from './pages/search-posts/search-posts';

export const routes: Routes = [
  { path: 'create', component: CreatePost },
  { path: 'posts', component: ListPosts },
  { path: 'search', component: SearchPosts },
  { path: '', redirectTo: 'posts', pathMatch: 'full' }
];


