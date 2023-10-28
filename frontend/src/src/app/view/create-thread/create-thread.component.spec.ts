import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateThreadComponent } from './create-thread.component';

describe('CreateThreadComponent', () => {
  let component: CreateThreadComponent;
  let fixture: ComponentFixture<CreateThreadComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateThreadComponent]
    });
    fixture = TestBed.createComponent(CreateThreadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
