import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomepageComponent } from './view/homepage/homepage.component';
import { ForumComponent } from './view/forum/forum.component';
import { ThreadComponent } from './view/thread/thread.component';
import { LoginComponent } from './view/login/login.component';
import { CreatePostComponent } from './view/create-post/create-post.component';
import { AdminComponent } from './view/admin/admin.component';
import { CreateThreadComponent } from './view/create-thread/create-thread.component';

const routes: Routes = [
  { path: '', redirectTo: '/', pathMatch: 'full' },
  { path: '', pathMatch: 'full', component: HomepageComponent },
  { path: 'login', component: LoginComponent },
  { path: 'forum/:id', component: ForumComponent },
  { path: 'forum/:id/:threadId/:pageNumber', component: ThreadComponent },
  { path: 'create-thread', component: CreateThreadComponent },
  { path: 'create-post', component: CreatePostComponent },
  { path: 'admin-portal', component: AdminComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
