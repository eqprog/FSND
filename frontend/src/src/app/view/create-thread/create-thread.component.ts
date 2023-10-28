import { HttpClient } from '@angular/common/http';
import { Component, DestroyRef, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { StateService, ViewState } from 'src/app/services/state.service';
import { Forum } from '../homepage/homepage.component';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { CreateThreadService } from 'src/app/services/create-thread/create-thread.service';
import { ForumService } from 'src/app/services/forum/forum.service';

@Component({
  selector: 'app-create-thread',
  templateUrl: './create-thread.component.html',
  styleUrls: ['./create-thread.component.scss']
})
export class CreateThreadComponent implements OnInit {

  protected forum!: Forum | null;
  protected form!: FormGroup;

  constructor(
    private stateService: StateService,
    private forumService: ForumService,
    private destroyRef: DestroyRef
  ) { }

  ngOnInit(): void {
    this.getState();
    this.form = this.forumService.getNewThreadForm();
  }

  private getState(): void {
    this.stateService.getState().pipe(takeUntilDestroyed(this.destroyRef)).subscribe((state: ViewState) => {
      this.forum = state.forum
      console.log('will create thread in forum', this.forum?.id);
    })
  }

  public submitThread(): void {
    this.forumService.postForumThread(this.form);
  }
}
