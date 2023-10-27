import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { StateService, ViewState } from '../state.service';
import { ForumResponse, Thread } from 'src/app/view/forum/forum.component';
import { BehaviorSubject, Subscription, take } from 'rxjs';
import { AbstractControl, FormControl, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../auth/auth-service.service';

@Injectable({
  providedIn: 'root'
})
export class ForumService {

  private loading: boolean = false;
  private threads: BehaviorSubject<Thread[]> = new BehaviorSubject<Thread[]>([]);
  private responseSubscription!: Subscription;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private stateService: StateService,
    private auth: AuthService
  ) { }

  public getForum(id: string): void {
    if (!id || this.loading) {
      return;
    }
    console.log('getting forum', id)
    this.loading = true;
    this.responseSubscription = this.http.get<ForumResponse>(`http://127.0.0.1:5000/forum/${id}`).pipe(take(1)).subscribe((response: ForumResponse) => {
      console.log(response);
      this.loading = false;
      this.stateService.setState({ forum: response.forum })
      this.threads.next(response.threads);
      this.responseSubscription.unsubscribe();
    })
  }

  public forumThreads(): BehaviorSubject<Thread[]> {
    return this.threads;
  }

  public getNewThreadForm(): FormGroup {
    return new FormGroup({
      title: new FormControl<string>('', { validators: [Validators.required, Validators.minLength(10), Validators.maxLength(36)]}),
      content: new FormControl<string>('', { validators: [Validators.required, Validators.minLength(20), Validators.maxLength(1024)]})
    });
  }

  public postForumThread(form: FormGroup): void {
    if (form.invalid) {
      return;
    }
    const title: AbstractControl | null = form.get('title');
    const content: AbstractControl | null = form.get('content');
    const state: ViewState = this.stateService.getCurrentState();
    if (!title || !content || !state?.forum?.id) {
      return;
    }

    this.http.post(`http://127.0.0.1:5000/forum/${state.forum.id}`, { ...form.value, user_id: 2 }, {
      headers: this.auth.getHeaders()
    }).pipe(take(1)).subscribe((response: any) => {
      console.log(response)
      if (response.thread) {
        this.router.navigateByUrl(`/forum/${response.thread?.forumId}/${response.thread?.id}/1`);
      }
    })

  }
}
