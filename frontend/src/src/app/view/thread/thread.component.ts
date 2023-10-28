import { HttpClient } from '@angular/common/http';
import { Component, DestroyRef, Inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { ForumService } from 'src/app/services/forum/forum.service';
import { StateService, ViewState } from 'src/app/services/state.service';
import { Post, Thread } from '../forum/forum.component';
import { ThreadPageResponse, ThreadService } from 'src/app/services/thread/thread.service';
import { Forum } from '../homepage/homepage.component';
import { take } from 'rxjs';
import { AuthService } from 'src/app/services/auth/auth-service.service';
import { API_URL } from 'src/app/app.module';

@Component({
  selector: 'app-thread',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss']
})
export class ThreadComponent implements OnInit {

  protected thread: Thread | null = null;
  protected forum: Forum | null = null;
  protected threadResponse!: ThreadPageResponse

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private stateService: StateService,
    private forumService: ForumService,
    private threadService: ThreadService,
    private destroyRef: DestroyRef,
    @Inject(API_URL) private apiUrl: string,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    const threadId: string | null = this.route.snapshot.paramMap.get('threadId');
    if (!threadId) {
      return;
    }
    const pageNumber: string | null = this.route.snapshot.paramMap.get('pageNumber');
    if (!pageNumber) {
      return;
    }
    this.getCurrentState(threadId, pageNumber);
    if (!this.forum) {
      const forumId: string | null = this.route.snapshot.paramMap.get('id')
      if (forumId) {
        this.forumService.getForum(forumId);
      }
    }
    if (!this.thread) {
      this.threadService.getThread(threadId);
    }
  }

  private getCurrentState(threadId: string, pageNumber: string): void {
    this.stateService.getState().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((state: ViewState) => {
      console.log('state', state);
      if (this.thread !== state.thread) {
        this.thread = state.thread;
        this.getCurrentPage();
        this.getThreadPage(threadId, pageNumber);
      }
      this.forum = state.forum;
      console.log(this.thread);
    })
  }

  private getThreadPage(id: string, pageNumber: string): void {
    this.threadService.getThreadPage(id, pageNumber);
  }

  private getCurrentPage(): void {
    this.threadService.currentPage().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((response: ThreadPageResponse | null) => {
      if (response) {
        console.log('thread page response', response)
        this.threadResponse = response
      }
    })
  }

  public goToForum(): void {
    this.router.navigateByUrl(`forum/${this.forum?.id}`)
  }

  public post(): void {
    this.router.navigateByUrl('create-post');
  }

  public editPost(id?: number): void {
    const params: Record<string, unknown> = { edit: 'true' };
    if (id ?? false) {
      params['postId'] = `${id}`;
    }
    this.router.navigate(['create-post', params])
  }

  public markForDeletion(post: Post): void {
    post.markedForDeletion = true;
  }

  public confirmDelete(post: Post): void {
    const params: Record<string, unknown> = { edit: 'true' };
    if (post.id ?? false) {
      params['postId'] = `${post.id}`;
    }
    this.http.delete<{status: 'SUCCESS' | 'FAILURE'}>(`${this.apiUrl}/threads/${this.thread?.id}`, {headers: this.auth.getHeaders(), body: { post_id: post.id }}).pipe((take(1))).subscribe({ next: (response: { status: 'SUCCESS' | 'FAILURE' }) => {
      if (response.status === 'SUCCESS') {
        this.getThreadPage(this.route.snapshot.paramMap.get('threadId')!, this.route.snapshot.paramMap.get('pageNumber')!)
      } else {
        post.content = 'Error deleting post! Oops'
        post.markedForDeletion = false;
      }
    }, error: () => {
      post.markedForDeletion = false;
    }});
  }

  public cancelDelete(post: Post): void {
    post.markedForDeletion = false;
  }


}
