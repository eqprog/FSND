import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, Validators } from '@angular/forms';
import { StateService, ViewState } from '../state.service';

@Injectable({
  providedIn: 'root'
})
export class CreateThreadService {

  constructor(
    private http: HttpClient,
    private stateService: StateService
  ) { }

  public getFormGroup(): FormGroup {
    return new FormGroup({
      title: new FormControl<string>('', { validators: [Validators.required, Validators.minLength(10), Validators.maxLength(36)]}),
      content: new FormControl<string>('', { validators: [Validators.required, Validators.minLength(20), Validators.maxLength(1024)]})
    });
  }

  public createThread(form: FormGroup): void {
    if (form.invalid) {
      return;
    }
    const title: AbstractControl | null = form.get('title');
    const content: AbstractControl | null = form.get('content');
    const state: ViewState = this.stateService.getCurrentState();
    if (!title || !content || !state?.forum?.id) {
      return;
    }

    // this.http.post(`http://127.0.0.1:5000/forum`)


  }
}
