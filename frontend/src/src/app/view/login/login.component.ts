import { Component } from '@angular/core';
import { AuthService } from 'src/app/services/auth/auth-service.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  public loginUrl!: string;

  constructor(public auth: AuthService) {
    this.loginUrl = auth.build_login_link();
  }


}
