import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomepageComponent } from './view/homepage/homepage.component';
import { LoginComponent } from './view/login/login.component';
import { ForumComponent } from './view/forum/forum.component';
import { ThreadComponent } from './view/thread/thread.component';
import { PostComponent } from './components/post/post.component';
import { CreatePostComponent } from './view/create-post/create-post.component';
import { AdminComponent } from './view/admin/admin.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AllForumsComponent } from './view/all-forums/all-forums.component';
import { CreateThreadComponent } from './view/create-thread/create-thread.component';
import { StateService } from './services/state.service';

@NgModule({
  declarations: [
    AppComponent,
    HomepageComponent,
    LoginComponent,
    ForumComponent,
    ThreadComponent,
    PostComponent,
    CreatePostComponent,
    AdminComponent,
    AllForumsComponent,
    CreateThreadComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [StateService],
  bootstrap: [AppComponent]
})
export class AppModule { }
