import { TestBed } from '@angular/core/testing';

import { CreateThreadService } from './create-thread.service';

describe('CreateThreadService', () => {
  let service: CreateThreadService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CreateThreadService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
