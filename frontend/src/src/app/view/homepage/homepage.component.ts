import { HttpClient } from '@angular/common/http';
import { Component, Inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { take } from 'rxjs';
import { API_URL } from 'src/app/app.module';

export type Forum = {
  id: number | null;
  name: string;
  description: string;
}

type ForumsResponse = {
  status: string;
  forums: Forum[];
}

@Component({
  selector: 'app-homepage',
  templateUrl: './homepage.component.html',
  styleUrls: ['./homepage.component.scss']
})
export class HomepageComponent implements OnInit {

  protected forumResponse: ForumsResponse | null = null;

  constructor(
    public router: Router,
    @Inject(API_URL) private apiUrl: string,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.getAllForums();
  }

  protected getAllForums(): void {
    const subscription = this.http.get<ForumsResponse>(`${this.apiUrl}/`).pipe(take(1)).subscribe((response: ForumsResponse) => {
      this.forumResponse = response;
      console.log(response)
      subscription.unsubscribe();
    });
  }

  protected viewForum(id?: number | null): void {
    if (id) {
      this.router.navigateByUrl(`forum/${id}`)
    }
  }
}
