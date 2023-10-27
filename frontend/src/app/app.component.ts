import { Component, OnInit } from '@angular/core';
import { AuthService } from './services/auth/auth-service.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'frontend';

  constructor(private auth: AuthService) {}

  ngOnInit(): void {
    this.auth.load_jwts();
    this.auth.check_token_fragment();
  }
}
