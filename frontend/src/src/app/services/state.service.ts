import { Injectable } from '@angular/core';
import { Forum } from '../view/homepage/homepage.component';
import { Thread } from '../view/forum/forum.component';
import { BehaviorSubject } from 'rxjs';

export type ViewState = {
  forum: Forum | null,
  thread: Thread | null
}

@Injectable({
  providedIn: 'root'
})
export class StateService {

  private state: ViewState = { forum: null, thread: null };
  private stateSubject: BehaviorSubject<ViewState> = new BehaviorSubject<ViewState>({ forum: null, thread: null});

  constructor() { }

  public setState(state: { forum?: Forum, thread?: Thread }) {
    if (state.forum) {
      this.state.forum = state.forum
    }
    if (state.thread) {
      this.state.thread = state.thread;
    }
    this.updateState();
    console.log(this.state);
  }

  private updateState(): void {
    this.stateSubject.next(this.state);
  }

  public getState(): BehaviorSubject<ViewState> {
    return this.stateSubject;
  }

  public getCurrentState(): ViewState {
    return this.state;
  }


}
