import { TestBed } from '@angular/core/testing';

import { ThreadService } from './thread.service';

describe('ThreadServiceService', () => {
  let service: ThreadService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ThreadService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
