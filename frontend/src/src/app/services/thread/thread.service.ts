import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BehaviorSubject, Subscription, take } from 'rxjs';
import { Post, Thread } from 'src/app/view/forum/forum.component';
import { StateService } from '../state.service';
import { API_URL } from 'src/app/app.module';

export type ThreadPageResponse = {
  status: 'SUCCESS' | 'FAILURE',
  page: {
    forumId: number;
    id: number;
    title: number;
    dateCreated: string;
    posts: Array<Post>,
    locked: boolean;
  }
}

export type ThreadResponse = {
  status: 'SUCCESS' | 'FAILURE';
  thread: Thread;
}

@Injectable({
  providedIn: 'root'
})
export class ThreadService {

  private loading: boolean = false;
  private thread: Thread | null = null;
  private threadPage: BehaviorSubject<ThreadPageResponse | null> = new BehaviorSubject<ThreadPageResponse | null>(null);
  private responseSubscription!: Subscription;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    @Inject(API_URL) private apiUrl: string,
    private stateService: StateService
  ) { }

  public getThreadPage(id: string, pageNumber: string) {
    if (!id || this.loading) {
      return;
    }

    console.log('getting thread page', id);
    this.loading = true;
    this.responseSubscription = this.http.get<ThreadPageResponse>(`${this.apiUrl}/threads/${id}/${pageNumber}`).pipe(take(1)).subscribe((response: ThreadPageResponse) => {
      this.loading = false;
      console.log(response)
      this.threadPage.next(response);
    })
  }

  public getThread(id: string): void {
    if (!id || this.loading) {
      return;
    }

    console.log('getting thread page', id);
    this.loading = true;
    this.responseSubscription = this.http.get<ThreadResponse>(`${this.apiUrl}/threads/${id}`).pipe((take(1))).subscribe((response: ThreadResponse) => {
      this.loading = false;
      this.thread = response.thread;
      this.stateService.setState({thread: response.thread })
    })
  }

  public currentPage(): BehaviorSubject<ThreadPageResponse | null> {
    return this.threadPage;
  }
}
