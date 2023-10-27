import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { take } from 'rxjs';
import { AuthService } from 'src/app/services/auth/auth-service.service';

type AdminView = 'forum' | 'ban';


type BanType = 'PROBATION' | 'PERMANENT' | 'REMOVE'
type ProbationDuration = '1 HOUR' | '2 HOURS' | '6 HOURS' | '12 HOURS' | '1 DAY' | '3 DAYS' | '1 WEEK' | '2 WEEKS' | '1 MONTH' | '2 MONTHS' | '3 MONTHS' | '6 MONTHS';

export type StatusMessage = { status: 'SUCCESS' | 'FAILURE', message: string };
export type User = {
  id: number,
  name: string,
  role: string,
  status: string,
  probationStartDate: string,
  probationEndDate: string
}

export type UserListResponse = {
  status: 'SUCCESS' | 'FAILURE',
  users: User[]
}

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {


  protected view: AdminView = 'forum';
  protected banTypes: BanType[] = ['PROBATION', 'PERMANENT', 'REMOVE'];
  protected banTypeSelected!: BanType;
  protected probationDurationOptions: ProbationDuration[] = ['1 HOUR', '2 HOURS', '6 HOURS', '12 HOURS', '1 DAY', '3 DAYS', '1 WEEK', '2 WEEKS', '1 MONTH', '2 MONTHS', '3 MONTHS', '6 MONTHS'];

  protected forms: Record<AdminView, FormGroup> = {
    forum: new FormGroup({
      name: new FormControl(null, { validators: [Validators.required,
        // Validators.minLength(3),
        Validators.maxLength(36)] }),
      description: new FormControl(null, { validators: [Validators.required,
        // Validators.minLength(20),
        Validators.maxLength(120)] })
    }),
    ban: new FormGroup({
      user: new FormControl<string>('', { validators: [Validators.required] }),
      type: new FormControl<BanType | null>(null, { validators: [Validators.required] }),
      reason: new FormControl<string>('', { validators: [Validators.required] })
   })
  };

  protected serverResponse: StatusMessage | null = null;
  protected userListResponse: UserListResponse | null = null;
  protected selectedUser: User | null = null;

  constructor(private http: HttpClient, private auth: AuthService) {}

  ngOnInit(): void {
    this.getUserList();
  }

  protected getUserList(): void {
    const subscription = this.http.get<UserListResponse>('http://127.0.0.1:5000/admin/users', { headers: this.auth.getHeaders()}).pipe(take(1)).subscribe((response: UserListResponse) => {
      if (response.status === 'SUCCESS') {
        this.userListResponse = response;
      } else {
        this.userListResponse = {
          status: 'FAILURE',
          users: []
        }
      }
      subscription.unsubscribe();
    })
  }

  protected selectAction(formType: AdminView): void {
    this.view = formType;
  }

  protected selectBanType(): void {
    this.banTypeSelected = this.forms['ban'].get('type')?.value;
    if (this.banTypeSelected === 'PROBATION') {
      this.forms['ban'].addControl('duration', new FormControl<ProbationDuration>('1 HOUR', { validators: [Validators.required] }));
    } else {
      this.forms['ban'].removeControl('duration');
    }
  }

  protected submitForm(formType: AdminView): void {
    // button state is set in the DOM. Still checking validity if an outside script has enabled the button somehow
    if (this.forms[formType].valid) {
      if (formType === 'forum') {
        this.submitCreateForum(this.forms[formType].value)
      }
      if (formType === 'ban') {
        this.submitUserBan(this.forms[formType].value)
      }
    }
  }

  private submitCreateForum(requestBody: {}): void {
    console.log('form submitted');
    const subscription = this.http.post<StatusMessage>('http://127.0.0.1:5000/admin/create/forum', requestBody, {
      headers: this.auth.getHeaders(),
    }).pipe(take(1)).subscribe((response: StatusMessage) => {
      this.serverResponse = response;
      subscription.unsubscribe();
    });
  }

  private submitUserBan(banRequest: any): void {
    const request = {
      id: this.selectedUser?.id,
      type: banRequest['type'],
      reason: banRequest['reason'],
      duration: banRequest['duration'] || undefined
    }

    const subscription = this.http.post<StatusMessage>('http://127.0.0.1:5000/admin/ban-user', request, {
      headers: { 'Content-Type': 'application/json' }
    }).pipe(take(1)).subscribe((response: StatusMessage) => {
      this.serverResponse = response;
      subscription.unsubscribe();
    })
  }

  protected userSelected(): void {
    const userName = this.forms['ban']?.get('user')?.value;
    if (userName) {
      this.selectedUser = userName && this.userListResponse?.users ? this.userListResponse.users.find((user: User) => user.name === userName) || null : null;
    }
    console.log(this.selectedUser);
  }

  protected resetViewFromResponse(): void {
    this.serverResponse = null;
  }

}
