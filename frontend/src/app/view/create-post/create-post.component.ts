import { HttpClient } from '@angular/common/http';
import { Component, DestroyRef, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import { interval, switchMap, take, takeWhile } from 'rxjs';
import { StateService, ViewState } from 'src/app/services/state.service';
import { ThreadPageResponse, ThreadService } from 'src/app/services/thread/thread.service';
import { Post } from '../forum/forum.component';
import { AuthService } from 'src/app/services/auth/auth-service.service';

@Component({
  selector: 'app-create-post',
  templateUrl: './create-post.component.html',
  styleUrls: ['./create-post.component.scss']
})
export class CreatePostComponent implements OnInit {

  public state: ViewState;
  public editMode: boolean = false;
  public postId: number | null = null;
  public form: FormGroup | null = null;
  public threadId: number | null = null;
  public status!: 'SUCCESS' | 'FAILURE';
  public loadingDots: string[] = ['.'];
  public error!: boolean;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private stateService: StateService,
    private threadService: ThreadService,
    private destroyRef: DestroyRef,
    private auth: AuthService
  ) {
    this.state = this.stateService.getCurrentState();
    if (!this.state) {
      return;
    }
    this.route.paramMap.pipe(take(1)).subscribe((params: ParamMap) => {
      this.editMode = params.get('edit') === 'true';
      this.postId = Number(params.get('postId')) || null;
    });
    if (this.editMode && !this.postId) {
      return;
    }
    let content: string = '';
    this.threadService.currentPage().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((response: ThreadPageResponse | null) => {
      if (response) {
        this.threadId = response.page.id
        const post: Post | undefined = response.page.posts.find((post: Post) => post.id === this.postId)
        content = this.editMode && post ? post.content : content;
      }
    })
    this.form = new FormGroup({
      content: new FormControl<string>(content)
    })
  }

  ngOnInit(): void {

  }

  protected goToForum(): void {
    this.router.navigateByUrl(`forum/${this.state?.forum?.id}`);
  }

  protected submitForm(): void {
    if (this.editMode) {
      this.http.patch<{ status: 'SUCCESS' | 'FAILURE'}>(`http://127.0.0.1:5000/threads/${this.threadId}`, {
        post_id: this.postId,
        content: this.form?.get('content')?.value,
      }, {
        headers: this.auth.getHeaders()
      }).pipe(take(1)).subscribe({ next: (response) => {
        this.status = response.status;
        if (response.status === 'SUCCESS') {
          this.error = false;
          this.activateLoadingDots();
        }
      }, error: (response) => {
        this.error = true;
      }})
    } else {
      // create post
      this.http.post<{ status: 'SUCCESS' | 'FAILURE'}>(`http://127.0.0.1:5000/threads/${this.threadId}`, {
        content: this.form?.get('content')?.value,
      }, {
        headers: this.auth.getHeaders()
      }).pipe(take(1)).subscribe({ next: (response) => {
        this.status = response.status;
        if (response.status === 'SUCCESS') {
          this.error = false;
          this.activateLoadingDots();
        }
      }, error: (response) => {
        this.error = true;
      }})
    }
  }

  protected activateLoadingDots(): void {
    interval(500).pipe(takeWhile(() => this.loadingDots.length < 5))
    .subscribe({
      next: () => this.loadingDots.push('.'),
      complete: this.navigateToThread.bind(this)
    })
  }

  protected navigateToThread(): void {
    this.router.navigateByUrl(`forum/${this.state?.thread?.forumId}/${this.state?.thread?.id}/${this.state?.thread?.pages}`);
  }
}
