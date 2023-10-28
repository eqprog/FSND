import { Component, DestroyRef, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Forum } from '../homepage/homepage.component';
import { HttpClient } from '@angular/common/http';
import { take } from 'rxjs';
import { StateService, ViewState } from 'src/app/services/state.service';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { ForumService } from 'src/app/services/forum/forum.service';


export type Page = {
  id: number;
  thread_id: number;
  page_number: number;
  posts?: Post[]
}

export type Thread = {
  id: number,
  forumId: number,
  title: string;
  user_id: string;
  dateCreated: string;
  locked: boolean;
  pages?: number

}

export type Post = {
  id: number;
  user_id: number;
  user_name: string;
  content: string;
  dateCreated: string;
  dateEdited?: string;
  markedForDeletion?: boolean;
}

export type ForumResponse = {
  status: 'SUCCESS' | 'FAILURE';
  forum: Forum;
  threads: Thread[]
}

@Component({
  selector: 'app-forum',
  templateUrl: './forum.component.html',
  styleUrls: ['./forum.component.scss']
})
export class ForumComponent implements OnInit {

  protected forum: Forum | null = null;
  protected threads: Thread[] = []

  private loading: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private stateService: StateService,
    private forumService: ForumService,
    private destroyRef: DestroyRef
  ) { }

  ngOnInit(): void {
    const id: string | null = this.route.snapshot.paramMap.get('id');
    if (!id) {
      return;
    }
    this.getCurrentState();
    this.getForumThreads();
    this.getForumInfo(id);



    // const id = this.route.snapshot.paramMap.get('id');
    // if (id) {
    //   const subscription = this.http.get<ForumResponse>(`${this.apiUrl}/forum/${id}`).pipe(take(1)).subscribe((response: ForumResponse) => {
    //     if (response.status === 'SUCCESS') {
    //       this.forum = response.forum;
    //       this.threads = response.threads || [];
    //       this.stateService.setState({ forum: response.forum });
    //       console.log(this.forum);
    //       console.log(this.threads)
    //     } else {
    //       this.forum = null;
    //       this.threads = [];
    //     }
    //   })
    // }

  }

  private getForumInfo(id: string): void {
    this.forumService.getForum(id);
  }

  private getCurrentState(): void {
    this.stateService.getState().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((state: ViewState) => {
      if (this.forum !== state.forum) {
        this.forum = state.forum
      }
      console.log(this.forum);
    })
  }

  private getForumThreads(): void {
    this.forumService.forumThreads().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((threads: Thread[]) => {
      this.loading = false;
      console.log(threads);
      this.threads = threads;
    });
  }

  protected createThread(): void {
    if (this.forum?.id) {
      this.router.navigateByUrl(`create-thread`)
    }
  }

  protected viewThread(thread: Thread): void {
    if (thread) {
      this.router.navigateByUrl(`forum/${thread.forumId}/${thread.id}/1`)
    }
  }
}
